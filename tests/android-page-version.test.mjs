import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {runInNewContext} from "node:vm";

const root=resolve(import.meta.dirname,"..");
const html=readFileSync(resolve(root,"android/index.html"),"utf8");
const script=readFileSync(resolve(root,"android/latest.js"),"utf8");
const latest=JSON.parse(readFileSync(resolve(root,"android/latest.json"),"utf8"));

test("static public Android page matches the verified release manifest",()=>{
  assert.match(latest.version,/^\d+\.\d+\.\d+$/);
  assert.match(html,/id="android-latest-version"/);
  assert.match(html,/id="android-card-version"/);
  assert.match(html,/id="android-release-meta"/);
  assert.ok(html.includes("Android "+latest.version+" bêta"));
  assert.ok(html.includes("Version "+latest.version));
  assert.ok(!html.includes("Android 1.0.18"));
  assert.ok(!html.includes("Version 1.0.18"));
  assert.match(html,/src="\/android\/latest\.js\?v=\d+"/);
  assert.equal(latest.url,"https://github.com/zmehanna/gatekey-info/releases/download/android-latest/PrivateGateKey-Android.apk");
});

test("client displays future versions automatically from latest.json",async()=>{
  const fields=new Map([
    ["android-latest-version",{textContent:"Android "+latest.version+" bêta"}],
    ["android-card-version",{textContent:"Version "+latest.version}],
    ["android-release-meta",{textContent:"Dernière publication : 24 novembre 2026"}],
    ["try-android",{removeAttribute(){},setAttribute(){}}],
    ["emulator-status",{textContent:""}],
  ]);
  const download={href:"",setAttribute(){}};
  const page={
    getElementById:id=>fields.get(id)??null,
    querySelector:selector=>selector==="a.download"?download:null,
    addEventListener(){},visibilityState:"visible"
  };
  const next={...latest,version:"1.0.30",publishedAt:"2026-11-25T08:01:00Z"};
  const calls=[];
  const scope={
    document:page,window:{location:{href:"https://privategatekey.com/android/"},addEventListener(){}},
    navigator:{onLine:true},setInterval(){},URL,Date,Intl,
    console:{warn(){},debug(){}},
    fetch:async (url,opts={})=>{
      calls.push({url,opts});
      if(url.includes("latest.json"))return {
        ok:true,json:async()=>next,text:async()=>JSON.stringify(next)
      };
      if(url.includes("latest.js"))return {ok:true,text:async()=>script};
      return {ok:false};
    }
  };
  runInNewContext(script,scope);
  for(let i=0;i<12;i++)await Promise.resolve();
  assert.equal(fields.get("android-latest-version").textContent,"Android 1.0.30 bêta");
  assert.equal(fields.get("android-card-version").textContent,"Version 1.0.30");
  assert.equal(download.href,latest.url);
  assert.match(fields.get("android-release-meta").textContent,/25 novembre 2026/);
  assert.ok(calls.some(call=>call.url.includes("latest.json?_v=")&&call.opts.cache==="no-store"));
});

test("the auto-refresh watcher remains active for a changed manifest",()=>{
 assert.match(script,/function watchAndroidPageUpdates\(\)/);
 assert.match(script,/version !== baselineVersion/);
 assert.match(script,/window\.location\.replace\(url\.href\)/);
});
