## GitHub Copilot Chat

- Extension Version: 0.29.1 (prod)
- VS Code: vscode/1.102.0
- OS: Mac

## Network

User Settings:
```json
  "github.copilot.advanced.debug.useElectronFetcher": true,
  "github.copilot.advanced.debug.useNodeFetcher": false,
  "github.copilot.advanced.debug.useNodeFetchFetcher": true
```

Environment Variables:
- http_proxy=http://127.0.0.1:3128
- https_proxy=http://127.0.0.1:3128
- no_proxy=127.0.0.1,127.0.0.0/8,::1,*.zohomeeting.com,*.zohoassist.com,avcliq.zoho.com,.zohomeeting.com,.zohoassist.com,*.zohopublic.com,*.zohopublic.in,*.zohopublic.eu,*.zohopublic.com.au,*.zohopublic.jp,*.zohopublic.ca,*.zohopublic.sa,us4-wss-accl.zoho.com,us4-wss.zoho.com,us3-wss-accl.zoho.com,us3-wss.zoho.com,in2-wss.zoho.in,in1-wss.zoho.in,eu1-wss.zoho.eu,eu2-wss.zoho.eu,cn2-wss.zoho.com.cn,cn3-wss.zoho.com.cn,au1-wss.zoho.com.au,au2-wss.zoho.com.au,jp1-wss.zoho.jp,jp2-wss.zoho.jp,ca1-wss.zohocloud.ca,ca2-wss.zohocloud.ca,sa1-wss.zoho.sa,sa2-wss.zoho.sa,in1-wss.arattai.in,in2-wss.arattai.in,preus4-wss.zoho.com,preus3-wss.zoho.com,us4-wss-pop.zoho.com,us3-wss-pop.zoho.com,in2-wss-pop.zoho.in,in1-wss-pop.zoho.in,eu1-wss-pop.zoho.eu,eu2-wss-pop.zoho.eu,cn2-wss-pop.zoho.com.cn,cn3-wss-pop.zoho.com.cn,au1-wss-pop.zoho.com.au,au2-wss-pop.zoho.com.au,jp1-wss-pop.zoho.jp,jp2-wss-pop.zoho.jp,ca1-wss-pop.zohocloud.ca,ca2-wss-pop.zohocloud.ca,sa1-wss-pop.zoho.sa,sa2-wss-pop.zoho.sa,in2-prewss-pop.zoho.in,in1-prewss-pop.zoho.in,us4-wss-vod.zoho.com,us3-wss-vod.zoho.com,in2-wss-vod.zoho.in,in1-wss-vod.zoho.in,eu1-wss-vod.zoho.eu,eu2-wss-vod.zoho.eu,cn2-wss-vod.zoho.com.cn,cn3-wss-vod.zoho.com.cn,au1-wss-vod.zoho.com.au,au2-wss-vod.zoho.com.au,jp1-wss-vod.zoho.jp,jp2-wss-vod.zoho.jp,ca1-wss-vod.zohocloud.ca,ca2-wss-vod.zohocloud.ca,sa1-wss-vod.zoho.sa,sa2-wss-vod.zoho.sa,in1-wss-vod.arattai.in,in2-wss-vod.arattai.in,us4-prewss-vod.zoho.com,us3-prewss-vod.zoho.com,*.zohoconference.com

Connecting to https://api.github.com:
- DNS ipv4 Lookup: 20.207.73.85 (10 ms)
- DNS ipv6 Lookup: ::ffff:20.207.73.85 (3 ms)
- Proxy URL: http://127.0.0.1:3128 (1 ms)
- Proxy Connection: 200 OK (54 ms)
- Electron fetch (configured): HTTP 403 (38 ms)
- Node.js https: HTTP 403 (127 ms)
- Node.js fetch: HTTP 403 (125 ms)

Connecting to https://api.business.githubcopilot.com/_ping:
- DNS ipv4 Lookup: 140.82.112.21 (1 ms)
- DNS ipv6 Lookup: ::ffff:140.82.112.21 (2 ms)
- Proxy URL: http://127.0.0.1:3128 (0 ms)
- Proxy Connection: 200 OK (641 ms)
- Electron fetch (configured): HTTP 200 (257 ms)
- Node.js https: HTTP 200 (1023 ms)
- Node.js fetch: HTTP 200 (910 ms)

## Documentation

In corporate networks: [Troubleshooting firewall settings for GitHub Copilot](https://docs.github.com/en/copilot/troubleshooting-github-copilot/troubleshooting-firewall-settings-for-github-copilot).