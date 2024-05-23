
# cloudflare_ddns

cloudflare dynamic dns client


### test
```
make install

source venv/bin/activate

make test
```
#### run individual test eg.
```
pytest -rA tests/test_config.py
```

### drone
```
edit .drone.yml workspace path, set to project pwd
```

### configuration file:

```
cp envs/env_sample envs/.env
```


### deployment

#### host (virtual env)

```
make install
run:  source venv/bin/activate && cloudflare_ddns
```


#### docker
```
make docker_image

run: ./run_container.sh
```

### crontab example
```
*/10 * * * * cd /home/user/projects/cloudflare_ddns && ./run_container.sh >/dev/null 2>&1

```