執行 server_main.py,等待 client 開啟

```bash
python server_main.py
```

執行 gui.py

```bash
python gui.py [your_file_path]
```

輸入想要傳輸的 file_path 後將開啟 pytq5 畫面

進入 pyqt5 畫面後,點選 SETUP 並按下播放鍵即開始進行檔案傳輸。

按下暫停鍵時，畫面會暫停播放並暫停傳輸。

按下 TEARDOWN 鍵後，即結束所有程序，並關閉 socket 及 server。
