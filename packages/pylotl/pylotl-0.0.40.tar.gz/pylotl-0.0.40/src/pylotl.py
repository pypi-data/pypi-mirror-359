import argparse
import asyncio
import http.cookiejar
import re
import urllib.parse
import urllib.request
from clear import clear

async def fetch(host):
    def fetch_html():
        try:
            fake_headers = {"Accept":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36","Accept-Encoding":"deflate","Accept-Language":"en-US,en;q=0.5","User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36","UPGRADE-INSECURE-REQUESTS":"1"}
            cookie_jar = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
            urllib.request.install_opener(opener)
            request = urllib.request.Request(url=host,headers=fake_headers,method="GET")
            response = urllib.request.urlopen(request,timeout=10)
            return response
        except:
            return None
    return await asyncio.to_thread(fetch_html)

async def pylotl(host,subdomain_bool):
    hits = {}
    web_host = f"http://{host}"
    visits = [web_host]
    links = [web_host]
    count = 0

    while True:
        try:
            count += 1
            print(f"CRAWLING WITH DEPTH OF: {count}")
            tasks = [fetch(link) for link in links]
            responses = await asyncio.gather(*tasks)
            skip = False
            old_visit_count = len(visits)
            for response in responses:
                if response:
                    content = response.read().decode(errors="ignore")
                   
                    if len(content) <= 25000000:
                        links = [i.rstrip("/") for i in list(dict.fromkeys(re.findall(r"(?:href|src|action|data|cite|poster|content|background|profile|manifest|srcset|ping)\s*=\s*[\"'](\S+?)(?=[\"'\\])",content)))] + [i.rstrip("/") for i in list(dict.fromkeys(re.findall(r"src\s*=\s*[\"\'](\S+?)(?=[\"\'\\])",content)))]
                        for link in links:
                            link = link.encode("ascii",errors="ignore").decode()
                            if link.startswith("http://") or link.startswith("https://"):
                                if urllib.parse.urlparse(web_host).netloc in urllib.parse.urlparse(link).netloc:
                                    new_link = link

                                else:
                                    continue

                            elif link.startswith("//"):
                                if urllib.parse.urlparse(web_host).netloc in urllib.parse.urlparse(urllib.parse.urlparse(response.url).scheme + ":" + link).netloc:
                                    new_link = urllib.parse.urlparse(response.url).scheme + ":" + link

                                else:
                                    continue

                            elif link.startswith("/") and not link.startswith("//"):
                                if urllib.parse.urlparse(web_host).netloc in urllib.parse.urlparse(f"{response.url.rstrip('/')}{link}").netloc:
                                    new_link = f"{response.url.rstrip('/')}{link}"

                                else:
                                    continue
                                
                            else:
                                if urllib.parse.urlparse(web_host).netloc in urllib.parse.urlparse(f"{response.url.rstrip('/')}/{link}").netloc:
                                    new_link = f"{response.url.rstrip('/')}/{link}"

                                else:
                                    continue

                            if not skip:
                                new_link = new_link.rstrip("/")
                                visits.append(new_link)
                                visits = list(dict.fromkeys(visits[:]))
                                links.append(new_link)
                                links = list(dict.fromkeys(links[:]))

            if old_visit_count == len(visits):
                break

        except:
            pass

    results = []
    if subdomain_bool:
        for visit in visits:
            if not re.search("[@]",visit):
                results.append(urllib.parse.urlparse(visit).netloc)

        results = list(dict.fromkeys(results[:]))
        results.sort()
        return results

    else:
        return visits

if __name__ == "__main__":
    clear()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-host",required=True)
    parser.add_argument("-subdomains",action="store_true")
    args = parser.parse_args()

    hits = asyncio.run(pylotl(args.host,args.subdomains))
    clear()
    for hit in hits:
        print(hit)
