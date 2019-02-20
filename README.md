# Cazador — the ssh-tunnel

<p align="center">
  <img src="https://raw.githubusercontent.com/bashkirtsevich-llc/cazador/master/static/.logo.png">
</p>

Cazador — is a simply ssh-tunnel for simplify connections. 

Can be used for:

1. experiments on localhost or local area network;
2. simplify access to remote ssh.

_Disclaimer_:
> **WARNING!**
>
> This software provide ssh-tunneling and password storing, it can be potentially dangerous! It's not recommended for using in real systems.


## Config

Config file — is a simply yml file with sections:
* `config` — application parameters;
  * `port` — server listen port (default `22`);
  * `allow_empty_passwords` — enable users without password;
  * `host_keys` — list of OpenSSH key-files;
* `users` — dictionary with `user_login: "password_hash"` pairs;
* `connections` — dictionary with ssh login credentials, each element contains next structures:
  * `host` — IP-address or hostname of destination ssh-server;
  * `port` — listen port of destination ssh-server (default `22`);
  * `username` — user login;
  * `password` — user password;
* `commands` — dictionary with names and shell-commands lists;
* `routes` — dictionary contains structures which provide relationship between `user` and `connection` with `command`.
  

### `config.yml` example

```yaml
config:
  port: 8022
  allow_empty_passwords: yes
  host_keys:
  - ssh_host_key
users:
  alpine:
  debian:
  admin: "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # sha256 of "password"
connections:
  docker:
    host: "127.0.0.1"
    username: "root"
    password: "password"
  local:
    host: "localhost"
    port: 22
    username: "user1"
    password: "password"
commands:
  alpine_docker:
  - "docker run -it --rm alpine ash"
  debian_docker:
  - "docker run -it --rm debian bash"
routes:
  alpine:
    connection: docker
    command: alpine_docker
  debian:
    connection: docker
    command: debian_docker
  admin:
    connection: local
```


## Startup

Required `Python 3.7+`

1. `pip install -r requirements`;
2. `exports CONFIG_PATH="/path/to/your/config.yml"`;
3. `python app.py`.

Or use docker

1. `docker build -t cazador .`;
2. `docker run -d -p 22:22 -e "CONFIG_PATH=/path/to/your/config.yml" -v /path/to/your/config.yml:/path/to/your/config.yml -v /path/to/your/ssh-keys:/path/to/your/ssh-keys cazador`;


# MIT-License

> Copyright (c) 2019 Bashkirtsevich LLC
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
> 
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.