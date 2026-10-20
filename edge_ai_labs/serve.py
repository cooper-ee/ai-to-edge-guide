"""Local CPU classifier service: train first, then start this module."""
import argparse
import hashlib
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import numpy as np
from .torch_labs import setup, load_classifier


def build_server(artifacts=Path('artifacts'), port=8000):
    torch = setup(42)
    model, mean, std = load_classifier(artifacts)
    digest = hashlib.sha256((Path(artifacts)/'classifier.pt').read_bytes()).hexdigest()
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, data):
            body = json.dumps(data,ensure_ascii=False,allow_nan=False).encode('utf8')
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            if self.path == '/health':
                self.reply(200,{'status':'ready','model_sha256':digest,'device':'cpu'})
            else:
                self.reply(404,{'error':'unknown endpoint'})
        def do_POST(self):
            if self.path != '/predict':
                self.reply(404,{'error':'unknown endpoint'})
                return
            try:
                self.connection.settimeout(5)
                size = int(self.headers.get('Content-Length','0'))
                if not 0 < size <= 16384:
                    raise ValueError('Body size must be 1..16384 bytes')
                data = json.loads(self.rfile.read(size).decode('utf8'))
                if not isinstance(data,dict) or set(data) != {'features'}:
                    raise ValueError('Expected exactly features')
                x = np.asarray(data['features'],dtype='float32')
                if x.ndim != 2 or x.shape[1] != 4 or not 1 <= len(x) <= 64 or not np.isfinite(x).all():
                    raise ValueError('Expected finite features [batch,4], batch in 1..64')
                with torch.inference_mode():
                    logits = model((torch.from_numpy(x)-mean)/std)
                    probabilities = torch.softmax(logits,-1).numpy()
                self.reply(200,{'predictions':probabilities.argmax(-1).tolist(),
                                'probabilities':probabilities.tolist(),'model_sha256':digest})
            except (ValueError,TypeError,UnicodeError,OverflowError) as e:
                self.reply(400,{'error':str(e)})
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--artifacts',type=Path,default=Path('artifacts'))
    p.add_argument('--port',type=int,default=8000)
    args = p.parse_args()
    server = build_server(args.artifacts,args.port)
    print(f'http://127.0.0.1:{server.server_port} /health /predict',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == '__main__': main()
