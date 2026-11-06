# Demo VP Index on the testbed

A FAIR Data Point in index mode at
<https://fair-testbed.eemcs.utwente.nl/demo-index>. Demonstrators register
their FDPs here, never in the production VP Index. D5 registers its notebook
here (step 4), and D11's FDPlight ping workflow points here.

## How it fits on the testbed

The testbed has one public host name and one certificate. The Caddy front
proxy of the pid-relay stack (`/opt/pid-relay/deploy`) holds ports 80 and 443
and routes by path. This stack is a separate compose project. Only its client
joins pid-relay's network (`pid-relay_default`), under the alias
`erdera-demo-index-client`, and the route lives in pid-relay's
`deploy/Caddyfile`.

| Service | What |
| --- | --- |
| `fdp` | `fairdata/fairdatapoint:1.22.2`, index mode, native triple store on a volume, published on `127.0.0.1:8083` for the server only |
| `fdp-store-init` | one-shot, hands the store volume to the FDP's user (uid 100) |
| `client` | `fairdata/fairdatapoint-client:1.18.1` with `PUBLIC_PATH=/demo-index` |
| `mongo` | `mongo:8.2.12` |

Settings: new entries are accepted and harvested without an admin step
(`INSTANCE_INDEXAUTOPERMIT`), pings need no authorisation, and the index does
not ping anywhere itself. Rate limit and deny list are the FDP defaults (10
pings per IP per 6 hours, `localhost` refused).

## Deploy

On the server, as a sudoer. The first command is only needed once.

```bash
sudo git clone https://github.com/luizbonino/erdera-demonstrators /opt/erdera-demonstrators
cd /opt/erdera-demonstrators/infra/demo-index && sudo ./deploy.sh
```

`deploy.sh` writes `.env` with a new JWT secret if there is none, starts the
stack, and runs `secure-defaults.sh`. That script replaces the passwords of
the two default accounts (`albert.einstein@example.com`, admin, and
`nikola.tesla@example.com`) with random ones, writes them to
`admin-credentials` (mode 600, not in git), and checks that the old admin
password is refused. Only then add the public route:

```bash
cd /opt/pid-relay
sudo git -c safe.directory=/opt/pid-relay fetch -q origin
sudo git -c safe.directory=/opt/pid-relay checkout origin/main -- deploy/Caddyfile
cd deploy && sudo docker compose up -d --no-deps --force-recreate caddy
```

This takes the Caddyfile alone from pid-relay's `main`, not the rest of that
repository. Caddy has to be recreated, not reloaded, because the Caddyfile is
a bind-mounted file and `git checkout` replaces it. The redirect service is
down for the few seconds that takes. Certificates are kept in the
`caddy_data` volume.

To update the index later: `git pull` in `/opt/erdera-demonstrators`, then
`sudo ./deploy.sh` again. The passwords are not touched a second time.

## After the first deploy

Log in at <https://fair-testbed.eemcs.utwente.nl/demo-index> with the admin
account from `admin-credentials`, then:

1. Edit the index record: title (it starts as "My FAIR Data Point"),
   description (it starts as lorem ipsum) and publisher. Use the client's
   form. Sending back the whole record from a GET through the API
   duplicates the triples the FDP generates itself.
2. Create your own admin account under Users, if you want one.

## Check

```bash
curl -s -H 'Accept: text/turtle' https://fair-testbed.eemcs.utwente.nl/demo-index | head
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"clientUrl": "https://example.github.io/my-fdp/fdp.ttl"}' \
  -w '%{http_code}\n' https://fair-testbed.eemcs.utwente.nl/demo-index
curl -s -H 'Accept: application/json' https://fair-testbed.eemcs.utwente.nl/demo-index/index/entries/all
```

A ping answers 204. The entry shows up as `ACCEPTED`, and as `ACTIVE` once
the metadata has been harvested.

## Tested

The whole stack, `deploy.sh`, `secure-defaults.sh` and the Caddy route were
run in Docker locally on 2026-11-06 before the first deploy. A ping for the
WP13.3 ProQolid FDP on GitHub Pages
(`https://erdera.github.io/WP13.3_document_based_fdp/sites/proqolid/eprovide_fdp.ttl`)
answered 204 at both `/demo-index` and `/demo-index/`, and the entry became
ACCEPTED and ACTIVE.
