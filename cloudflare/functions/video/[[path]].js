// 社友影片：從 R2（bucket rctsi-videos，binding VIDEOS）串流，支援 Range（拖曳進度條、iPhone 播放都需要）。
// 網址：/video/<檔名>.mp4，只允許英數與 -_ 的 .mp4 檔名。
export async function onRequestGet({ request, env, params }) {
  const parts = Array.isArray(params.path) ? params.path : [params.path];
  const key = parts.join("/");
  if (!/^[a-z0-9_-]+\.mp4$/i.test(key)) return new Response("Not found", { status: 404 });

  const rangeHeader = request.headers.get("range");
  let range;
  if (rangeHeader) {
    const m = /^bytes=(\d*)-(\d*)$/.exec(rangeHeader.trim());
    if (m) {
      if (m[1] === "" && m[2] !== "") range = { suffix: Number(m[2]) };
      else if (m[1] !== "") {
        const offset = Number(m[1]);
        range = m[2] !== "" ? { offset, length: Number(m[2]) - offset + 1 } : { offset };
      }
    }
  }

  const obj = await env.VIDEOS.get(key, range ? { range } : undefined);
  if (!obj) return new Response("Not found", { status: 404 });

  const headers = new Headers();
  obj.writeHttpMetadata(headers);
  headers.set("content-type", "video/mp4");
  headers.set("accept-ranges", "bytes");
  headers.set("etag", obj.httpEtag);
  headers.set("cache-control", "public, max-age=86400");

  if (range && obj.range) {
    const size = obj.size;
    let start, end;
    if ("suffix" in obj.range) { start = size - obj.range.suffix; end = size - 1; }
    else { start = obj.range.offset ?? 0; end = obj.range.length != null ? start + obj.range.length - 1 : size - 1; }
    headers.set("content-range", `bytes ${start}-${end}/${size}`);
    headers.set("content-length", String(end - start + 1));
    return new Response(obj.body, { status: 206, headers });
  }
  headers.set("content-length", String(obj.size));
  return new Response(obj.body, { status: 200, headers });
}

export async function onRequestHead(ctx) {
  const res = await onRequestGet(ctx);
  return new Response(null, { status: res.status, headers: res.headers });
}
