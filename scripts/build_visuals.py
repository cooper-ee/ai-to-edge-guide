"""Rebuild original SVG diagrams and GIFs. No network or borrowed paper images."""
from pathlib import Path
import html
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/'assets'
INK, TEAL, BLUE, ORANGE = '#142f43','#07878b','#3668d4','#e88a39'
FONT = '"Microsoft YaHei","Noto Sans CJK SC","PingFang SC",sans-serif'


def text(x,y,s,size=20,color=INK,weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(s)}</text>'


def box(x,y,w,h,title,lines=(),color=TEAL):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="white" stroke="{color}" stroke-width="1.5"/>'
    s += f'<rect x="{x}" y="{y}" width="5" height="{h}" rx="2" fill="{color}"/>'
    s += text(x+18,y+34,title,21,INK,700)
    for i,line in enumerate(lines): s+=text(x+18,y+62+i*25,line,15,'#526b7c')
    return s


def line(x1,y1,x2,y2,color=TEAL):
    return f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="2" marker-end="url(#arrow)"/>'


def svg(name,w,h,content,title):
    header=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="{TEAL}"/></marker></defs><g font-family=\'{FONT}\'>'
    (ASSETS/name).write_text(header+content+'</g></svg>',encoding='utf8')


def static_diagrams():
    s='<rect width="1280" height="420" rx="24" fill="#102d40"/>'
    for x in range(800,1280,45):
        for y in range(20,420,45): s+=f'<circle cx="{x}" cy="{y}" r="1.3" fill="#326075"/>'
    s+=text(58,65,'A  LEARNING  LAB  FOR  UNDERSTANDING  &  VERIFICATION',15,'#7bd6d0',600)
    s+=text(58,143,'从 AI 基础',53,'#ffffff',750)+text(58,211,'到端侧部署',53,'#ffffff',750)
    s+=text(60,262,'把公式变成实验，把模型变成可验证的系统。',23,'#bdd5df')
    for x,label in [(60,'18 课完整路线'),(260,'11 个可运行实验'),(480,'原创图示与交互')]:
        s+=f'<rect x="{x}" y="310" width="185" height="44" rx="22" fill="#20485c"/>'
        s+=text(x+17,338,label,17,'#e6f4f7')
    for i,(a,b,c) in enumerate([('01','MODEL','数学与学习'),('02','RUNTIME','推理与状态'),('03','EDGE','执行与系统')]):
        y=65+i*100
        s+=f'<rect x="900" y="{y}" width="305" height="82" rx="14" fill="#193d51" stroke="#366173"/>'
        s+=text(920,y+34,a,23,'#76d8cb',700)+text(968,y+32,b,20,'#ffffff',650)+text(968,y+59,c,16,'#b8d0d9')
    svg('cover.svg',1280,420,s,'从 AI 基础到端侧部署：理解、实验、验证')

    s='<rect width="1220" height="620" rx="22" fill="#f3f8fa"/>'+text(40,52,'一条主线，三条可选深化路线',29,INK,700)
    s+=text(40,83,'先建立正确性，再研究效率；先跑通小模型，再进入设备。',17,'#526b7c')
    nodes=[(40,125,'00–03 · 基础与交付',['数据 → 梯度 → 模型','PyTorch → ONNX 对照']),
           (430,125,'04–06 · 推理机制',['Transformer / KV Cache','量化误差与存储账本']),
           (820,125,'14–16 · 系统闭环',['HTTP / 基准 / 项目','原始数据与可复现报告']),
           (40,350,'07–08 · 应用支线',['检索与工具校验','本地模型与证据回答']),
           (430,350,'09–11 · 系统深化',['Serving / 编译器','GPU Kernel / 在线归一化']),
           (820,350,'12–13、17 · 端侧深化',['RKNN / RKLLM','混合架构与板端验证'])]
    s+=line(375,198,424,198)+line(765,198,814,198)
    for x in [207,597,987]: s+=line(x,270,x,343)
    for x,y,t,ls in nodes:s+=box(x,y,335,145,t,ls)
    s+=text(42,557,'CPU 实验已提供  ·  应用支线可跳过  ·  GPU/NPU 流程需对应硬件另测',19,TEAL,600)
    svg('roadmap.svg',1220,620,s,'按依赖组织的 AI 到端侧学习路线')

    s='<rect width="1100" height="690" rx="22" fill="#f3f8fa"/>'+text(40,50,'一次请求，穿过五层执行栈',28,INK,700)
    layers=[('应用与服务','请求 / 检索 / 工具 / 排队 / 超时'),('模型与状态','结构 / 权重 / tokenizer / KV 与递推状态'),('Runtime 与编译','加载 / 图优化 / 调度 / 内存分配'),('算子与 Kernel','GEMM / 归一化 / Attention / 布局'),('硬件与系统','CPU / GPU / NPU / 带宽 / 驱动 / 线程')]
    for i,(t,d) in enumerate(layers):
        y=88+i*102
        s+=box(40,y,700,82,t,[d],TEAL if i%2==0 else BLUE)
        if i<4:s+=line(780,y+60,780,y+114)
    s+=text(810,155,'每层都问：',21,TEAL,700)
    for i,t in enumerate(['输入输出是什么？','状态由谁拥有？','错误在哪里发生？','证据如何核查？']):s+=text(810,207+i*50,t,19)
    s+=text(43,652,'正确性 → 数值对照 → 任务质量 → 性能 → 稳定性',20,TEAL,600)
    svg('stack.svg',1100,690,s,'应用到硬件的五层知识体系')

    s='<rect width="1200" height="470" rx="22" fill="#f3f8fa"/>'+text(35,52,'导出不是终点：部署正确性的六道关',28,INK,700)
    labels=[('1 输入语义','预处理 / 模板'),('2 图结构','算子 / 属性'),('3 实际形状','新尺寸可执行'),('4 数值对照','误差 / 最坏样本'),('5 任务质量','准确率 / 引用'),('6 系统可用','内存 / 延迟')]
    for i,(t,d) in enumerate(labels):
        x=35+(i%3)*390;y=110+(i//3)*170
        s+=box(x,y,350,125,t,[d],TEAL if i<3 else BLUE)
        if i%3<2:s+=line(x+352,y+60,x+383,y+60)
    s+=line(1135,237,1135,270)+line(1135,270,210,270)+line(210,270,210,277)
    svg('deployment.svg',1200,470,s,'部署正确性的六道验证关卡')

    s='<rect width="1200" height="570" rx="22" fill="#f3f8fa"/>'+text(38,52,'Host 与 Board：转换和执行是两段工作',28,INK,700)
    for x,t,c in [(35,'HOST · 转换环境',TEAL),(675,'BOARD · 执行环境',BLUE)]:
        s+=f'<rect x="{x}" y="95" width="490" height="380" rx="20" fill="white" stroke="{c}"/>'
        s+=text(x+22,135,t,22,c,700)
    for y,t,d in [(160,'模型与契约','config / tokenizer / 预处理'),(260,'转换与量化','Toolkit / target / 校准数据'),(360,'产物与证据','artifact / SHA256 / 日志')]:s+=box(60,y,440,86,t,[d])
    for y,t,d in [(160,'Runtime 与驱动','版本 / ABI / BSP / 芯片'),(260,'执行与输出','输入张量 / 推理 / 后处理'),(360,'设备验收','数值 / 任务 / 内存 / 延迟')]:s+=box(700,y,440,86,t,[d],BLUE)
    s+=line(530,315,667,315)+text(536,285,'校验后传输',16,TEAL)
    s+=text(38,527,'转换成功 ≠ 加载成功 ≠ 数值正确 ≠ 满足任务与性能目标',21,TEAL,600)
    svg('host-board.svg',1200,570,s,'Host 转换与 Board 执行的兼容链路')

    s='<rect width="1050" height="580" rx="22" fill="#f3f8fa"/>'+text(40,52,'Roofline：先问受计算限制，还是受搬运限制',26,INK,700)
    s+=line(110,465,950,465)+line(110,465,110,110)
    s+='<path d="M130 440 L570 180 L930 180" fill="none" stroke="#07878b" stroke-width="7" stroke-linejoin="round"/>'
    s+='<path d="M570 180 L570 465" stroke="#9aafbb" stroke-dasharray="6 6"/>'
    s+=text(140,145,'有效性能（示意，非实测）',20)+text(640,160,'计算上限',20,TEAL,700)
    s+=text(220,310,'带宽 × 算术强度',23,TEAL,650)+text(410,510,'算术强度 FLOP / byte',22)
    s+=text(590,395,'拐点 = 计算上限 / 带宽',20,'#526b7c')
    s+=text(42,555,'比较之前固定工作负载、精度、存储层级与测量口径。',18,'#526b7c')
    svg('roofline.svg',1050,580,s,'Roofline 模型原创示意图')

    s='<rect width="1000" height="550" rx="22" fill="#f3f8fa"/>'+text(35,52,'在线 softmax：用三个状态合并分块',28,INK,700)
    for x,t,ls in [(35,'已读部分',['最大值 m','分母 ℓ / 加权和 a']),(365,'对齐指数基准',['m′ = max(m, m_block)','旧状态乘 exp(m − m′)']),(695,'合并新块',['加新块的指数与加权项','输出 = a′ / ℓ′'])]:s+=box(x,125,270,150,t,ls)
    s+=line(309,200,357,200)+line(639,200,687,200)
    s+=text(40,352,'不能把每个块各自归一化后直接拼接。',25,TEAL,700)
    s+=text(40,401,'必须让旧结果与新块使用同一个最大值基准。',22)
    s+=text(40,475,'数值参考：edge_ai_labs/math_labs.py · online_attention',17,'#526b7c')
    svg('online-softmax.svg',1000,550,s,'在线 softmax 合并分块状态')


def font(size,bold=False):
    candidates=[Path('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc'),
                Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
                Path('/System/Library/Fonts/PingFang.ttc')]
    for p in candidates:
        if p.exists():return ImageFont.truetype(str(p),size)
    raise RuntimeError('Install a CJK font; see build_visuals.py font candidates')


def frame(title,subtitle):
    im=Image.new('RGB',(900,470),'#f4f8fa');d=ImageDraw.Draw(im)
    d.text((28,21),title,font=font(27,True),fill=INK)
    d.text((28,64),subtitle,font=font(17),fill='#577080')
    return im,d


def save_gif(name,frames,duration=450):
    frames[0].save(ASSETS/name,save_all=True,append_images=frames[1:],duration=duration,loop=0,optimize=True,disposal=2)


def animations():
    frames=[]
    for step in range(8):
        im,d=frame('因果注意力 · 当前 token 能读取谁？',f'位置 {step+1}：只允许看到自己与过去；上三角的未来信息被屏蔽。')
        x0,y0,cell=230,120,35
        for i in range(8):
            d.text((x0-35,y0+i*cell+5),str(i+1),font=font(16),fill=INK)
            for j in range(8):
                color='#e4eaf0' if j>i else '#d4e9e9'
                if i==step:color=TEAL if j<=i else '#f5dfcd'
                d.rounded_rectangle((x0+j*cell,y0+i*cell,x0+(j+1)*cell-4,y0+(i+1)*cell-4),5,fill=color)
        d.text((550,150),'青色：当前行可读',font=font(20),fill=TEAL)
        d.text((550,198),'浅橙：当前行被屏蔽',font=font(20),fill='#b96a26')
        d.text((35,425),'行 = query 位置   ·   列 = key 位置   ·   颜色表示可见性，不表示实际权重',font=font(17),fill='#577080')
        frames.append(im)
    save_gif('attention.gif',frames,650)

    frames=[]
    for t in range(1,9):
        im,d=frame('KV Cache · 历史状态逐步追加',f'第 {t} 步：复用前 {t-1} 份 K/V，只计算并加入当前 token。')
        for row,label in [(0,'K'),(1,'V')]:
            y=160+row*80;d.text((60,y+10),label,font=font(29,True),fill=INK)
            for j in range(8):
                x=135+j*81
                fill=TEAL if j<t-1 else ORANGE if j==t-1 else '#e1e8ee'
                d.rounded_rectangle((x,y,x+65,y+55),9,fill=fill)
                if j<t:d.text((x+23,y+14),str(j+1),font=font(20,True),fill='white')
        d.text((60,345),'青色：已有状态     橙色：新状态     灰色：尚未生成',font=font(20),fill=INK)
        d.text((60,402),'标准全注意力 payload：2 × B × T × Hkv × dh × L × 每元素字节',font=font(18),fill='#577080')
        frames.append(im)
    save_gif('kv-cache.gif',frames,650)

    import sys
    sys.path.insert(0,str(ROOT))
    from edge_ai_labs.systems import simulate
    static=simulate([2,8,2,2,6,3],continuous=False)['trace']
    cont=simulate([2,8,2,2,6,3],continuous=True)['trace']
    colors=['#07878b','#3668d4','#c45e54','#b87e2e','#7358a5','#467850']
    frames=[]
    for tick in range(17):
        im,d=frame('静态批处理 vs 连续批处理',f'时间走到 tick {tick}：每格为一个 token 的抽象执行步，不代表真实毫秒。')
        for group,(title,trace) in enumerate([('静态：等整批结束',static),('连续：空槽立即补入',cont)]):
            y=135+group*135;d.text((30,y),title,font=font(20,True),fill=INK)
            for j in range(16):
                for slot in range(2):
                    active=trace[j] if j<len(trace) else []
                    fill=colors[active[slot]] if slot<len(active) and j<tick else '#e1e8ee'
                    x=275+j*36;yy=y+slot*37
                    d.rounded_rectangle((x,yy,x+30,yy+29),4,fill=fill)
        d.text((35,421),'固定长度 [2, 8, 2, 2, 6, 3] · 两个槽 · 无 prefill / 内存竞争的教学模拟',font=font(17),fill='#577080')
        frames.append(im)
    save_gif('batching.gif',frames,320)

    frames=[]
    scores,values=[1.,2.,3.,.5],[10.,20.,5.,30.]
    for step in range(1,5):
        im,d=frame('在线 softmax · 不存整行，也能算同一个结果',f'已经处理 {step}/4 个分数；按同一最大值基准累计分母与加权和。')
        m=max(scores[:step]);den=sum(math.exp(s-m) for s in scores[:step]);a=sum(math.exp(s-m)*v for s,v in zip(scores[:step],values[:step]))
        for j,s in enumerate(scores):
            x=55+j*200;fill=TEAL if j<step else '#dce6ec'
            d.rounded_rectangle((x,125,x+170,205),13,fill=fill)
            d.text((x+20,149),f's = {s:g}',font=font(23,True),fill='white' if j<step else INK)
        for x,label,num in [(55,'最大值 m',m),(330,'分母 ℓ',den),(605,'输出 a / ℓ',a/den)]:
            d.text((x,260),label,font=font(22),fill='#577080')
            d.text((x,305),f'{num:.4f}',font=font(36,True),fill=TEAL)
        d.text((55,420),'更新最大值时，旧分母与旧加权和都要乘 exp(m_old − m_new)。',font=font(18),fill=INK)
        frames.append(im)
    save_gif('online-softmax.gif',frames,1100)


if __name__ == '__main__':
    ASSETS.mkdir(parents=True,exist_ok=True)
    static_diagrams()
    animations()
    print('Generated 7 SVGs and 4 GIFs')
