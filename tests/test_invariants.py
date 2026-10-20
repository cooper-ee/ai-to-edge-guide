import json
from pathlib import Path
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import numpy as np
from edge_ai_labs.math_labs import dense_attention, online_attention, kv_bytes, quantize_dequantize, gradients
from edge_ai_labs.systems import simulate, call_tool, retrieve


class NumericalInvariants(unittest.TestCase):
    def test_gradient_finite_difference(self):
        self.assertLess(gradients()['max_gradient_error'],1e-8)

    def test_blocked_attention_extreme_logits_and_tail(self):
        rng = np.random.default_rng(2026)
        q,k,v = rng.normal(size=(3,17,8))
        q *= 100
        for causal in [True,False]:
            ref = dense_attention(q,k,v,causal)
            for block in [1,4,32]:
                np.testing.assert_allclose(online_attention(q,k,v,block,causal),ref,atol=1e-11)

    def test_causal_no_future_information(self):
        rng = np.random.default_rng(7)
        q,k,v = rng.normal(size=(3,13,8))
        ref = dense_attention(q,k,v,True)
        k[8:] += 500
        v[8:] -= 200
        np.testing.assert_allclose(dense_attention(q,k,v,True)[:8],ref[:8],atol=1e-12)

    def test_cache_memory_units_and_scaling(self):
        base = kv_bytes([24],[4],[64])
        self.assertEqual(base,50331648)
        self.assertEqual(kv_bytes([24],[4],[64],batch=2),2*base)
        self.assertEqual(kv_bytes([6],[4],[64])*4,base)
        with self.assertRaises(ValueError): kv_bytes([1],[2,3],[4])

    def test_quantization_zero_and_range(self):
        w = np.zeros((3,4))
        recon, scale = quantize_dequantize(w,4,True)
        np.testing.assert_array_equal(recon,w)
        self.assertTrue(np.isfinite(scale).all())
        w = np.array([[.1,.2,-.2],[10.,-20.,30.]])
        recon, scale = quantize_dequantize(w,8,True)
        self.assertTrue((np.abs(recon-w) <= scale/2+1e-10).all())

    def test_scheduler_conserves_tokens_and_slots(self):
        lengths = [1,9,2,4,1,1,3]
        for continuous in [True,False]:
            r = simulate(lengths,3,continuous)
            self.assertEqual(sum(map(len,r['trace'])),sum(lengths))
            self.assertTrue(all(len(t)<=3 for t in r['trace']))
            for i,n in enumerate(lengths):
                self.assertEqual(sum(i in t for t in r['trace']),n)
        self.assertEqual(simulate([])['makespan_ticks'],0)
        with self.assertRaises(ValueError): simulate([0])

    def test_tools_reject_unknown_and_extra_fields(self):
        for name,args,budget in [('shell',{},0),('get_model_info',{'model_id':'toy-mlp-v1','path':'x'},0),
                                 ('get_model_info',{'model_id':'toy-mlp-v1'},3)]:
            with self.assertRaises(ValueError): call_tool(name,args,budget)
        self.assertEqual(retrieve('ONNX 导出')[0]['id'],'D3')
        self.assertEqual(retrieve(''),[])


class ServiceIntegration(unittest.TestCase):
    def test_real_http_valid_and_invalid_requests(self):
        artifacts = Path('artifacts')
        if not (artifacts/'classifier.pt').exists():
            self.skipTest('Run --lab classifier to enable service integration test')
        from edge_ai_labs.serve import build_server
        server = build_server(artifacts,0)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(base+'/health',timeout=5) as r:
                self.assertEqual(json.load(r)['status'],'ready')
            req = Request(base+'/predict',data=json.dumps({'features':[[1,2,3,4]]}).encode(),
                          headers={'Content-Type':'application/json'})
            with urlopen(req,timeout=5) as r:
                result = json.load(r)
                self.assertEqual(len(result['predictions']),1)
                self.assertAlmostEqual(sum(result['probabilities'][0]),1.,places=5)
            req = Request(base+'/predict',data=b'{"features":[[1,2]]}')
            with self.assertRaises(HTTPError) as caught: urlopen(req,timeout=5)
            self.assertEqual(caught.exception.code,400)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == '__main__': unittest.main()
