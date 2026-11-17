// Send the old pages.dev address and www to https://keeperphoto.app, path for path.
// Shipped app builds link to keeper-photo-cleaner.pages.dev/privacy, so that link
// must land on the same page here. Preview deployments (<hash>.keeper-photo-cleaner.pages.dev)
// are left alone.
const CANONICAL = "keeperphoto.app";
const OLD_HOSTS = new Set(["keeper-photo-cleaner.pages.dev", "www.keeperphoto.app"]);

export async function onRequest({ request, next }) {
  const url = new URL(request.url);
  if (OLD_HOSTS.has(url.hostname)) {
    url.hostname = CANONICAL;
    url.protocol = "https:";
    url.port = "";
    return Response.redirect(url.toString(), 301);
  }
  return next();
}
