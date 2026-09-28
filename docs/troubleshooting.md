# 故障排除

程序找不到浏览器（如 Flatpak 等非标准安装方式）时，可以通过 `.env`（或同名环境变量）手动指定浏览器。这些是高级配置，配置向导不会询问，格式参考 [.env.example](../.env.example)。

## 方式一：指定浏览器可执行文件（推荐）

用 `BROWSER_EXECUTABLE_PATH` 指定浏览器的可执行文件，程序会照常自行启动和关闭浏览器，`HEADLESS` 和静音也照常生效。Flatpak 会为每个应用导出一个启动脚本，可以直接填这个路径（用户级安装在 `~/.local/share/flatpak/exports/bin/` 下）：

```env
BROWSER_EXECUTABLE_PATH=/var/lib/flatpak/exports/bin/com.microsoft.Edge
```

设置后 `BROWSER` 会被忽略。即使您已经开着同一个浏览器，程序也会使用独立的临时配置启动一个新实例，不会影响已打开的窗口。

## 方式二：连接自启动的浏览器（CDP）

自己启动浏览器并开启远程调试端口，再用 `CDP_ENDPOINT` 让程序连接它：

```bash
# 1. 启动浏览器（以 Flatpak 版 Edge 为例，必须使用独立的配置目录，否则调试端口会被已打开的实例忽略）
flatpak run com.microsoft.Edge \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.var/app/com.microsoft.Edge/fly-video-profile" \
  --mute-audio

# 2. 在 .env 中加入
CDP_ENDPOINT=http://127.0.0.1:9222
```

`CDP_ENDPOINT` 优先级最高，设置后 `BROWSER`、`HEADLESS` 和 `BROWSER_EXECUTABLE_PATH` 都会被忽略，静音等启动参数也需要像上面一样自己加。程序退出时只会断开连接，不会关闭您的浏览器。

> [!CAUTION]
> 调试端口开启期间，本机任何进程都可以完全控制该浏览器，用完请及时关闭。
