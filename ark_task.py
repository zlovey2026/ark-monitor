import json, time, urllib.request
from datetime import datetime, timezone, timedelta
CST=timezone(timedelta(hours=8))

TOKEN="8812425386:AAHoFPaNdDkn69_66kMpXwHrh8r52ejgB3E"
CHAT="-5410288785"
TG=f"https://api.telegram.org/bot{TOKEN}"
PROXY="0x8366a748E02F730911Cb5AB4fd049d2E1e0414b7"
LP="0xCAaF3c41a40103a23Eeaa4BbA468AF3cF5b0e0D8"
RPC_LIST=["https://bsc-dataseed.bnbchain.org","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://1rpc.io/bnb"]

def bj(): return datetime.now(CST).strftime("%H:%M")

def tg(text):
    try:
        d=json.dumps({"chat_id":CHAT,"text":text}).encode()
        urllib.request.urlopen(urllib.request.Request(f"{TG}/sendMessage",data=d,headers={"Content-Type":"application/json"}),timeout=10)
        return True
    except: return False

def call(to,data):
    for RPC in RPC_LIST:
        try:
            b=json.dumps({"jsonrpc":"2.0","method":"eth_call","params":[{"to":to,"data":data},"latest"],"id":1}).encode()
            r=urllib.request.Request(RPC,data=b,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(r,timeout=8) as x:
                res=json.loads(x.read()).get("result","")
                if res and res!="0x": return res
        except: continue
    return ""

def main():
    res=call(PROXY,"0xc3f909d4")
    if not (res and res!="0x"):
        print("read fail"); return
    h=res[2:]; w=[int(h[i:i+64],16) for i in range(0,len(h),64)]
    if len(w)<6:
        print("data err"); return
    mn,mx=w[4]/10000*100, w[5]/10000*100
    cur=round((mn+mx)/2,2)
    price=0
    pres=call(LP,"0x0902f1ac")
    if pres and pres!="0x":
        ph=pres[2:]
        usdt=int(ph[0:64],16)/1e18; ark=int(ph[64:128],16)/1e18
        if ark>0: price=usdt/ark
    try: s=json.load(open("ark_state.json"))
    except: s={"high":0,"low":100,"base":0,"last_send":0}
    now=time.time()
    s["high"]=max(s.get("high",0),mx); s["low"]=min(s.get("low",100),mn)
    if not s.get("base"): s["base"]=cur
    base=s["base"]; wave=(cur-base)/base*100 if base else 0
    need=(now-s.get("last_send",0)>=600)
    msg=(f"📊 当前系数：{cur:.2f}%\n🎯 基准系数：{base:.2f}%\n📐 波动幅度：{wave:+.2f}%\n📈 24小时最高：{s['high']:.2f}%\n📉 24小时最低：{s['low']:.2f}%\n💰 ARK价格：${price:.4f}\n🕐 更新时间：{bj()}")
    if need:
        if tg(msg):
            s["last_send"]=now; print("sent")
    else: print("skip")
    json.dump(s,open("ark_state.json","w"))

if __name__=="__main__": main()
