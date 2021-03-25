# トラブルシューティング

## Unreal Editorを使う上での問題

### Unreal Editorが起動しない

以下を確認してください

1. submodule 群が正しくチェックアウトできているか
2. エンジンバージョンが動作確認済みのものと同じか

### submodule PxArticulationLink が取得できない

PxArticulationLinkはUE4のリポジトリのフォークとして作っています。そのためEpicのUnrealEngineリポジトリにアクセスできるアカウントでないと404になります。

### 環境がスクリーンショットと比べて色々足りない

Alt-PでPlayしても色々不足しているようなら必要なアセットをEpic Games Launcherから追加しているか確認してください。

またエディタ起動直後は分割して保存されている地形等がロードされません。Playすればロードされますが、エディタでも表示するにはWindow -> Levels で TC_x?_y? とあるレベル群を選択し右クリックして、Load してください。

## その他一般

### CageClientが通信できない

ファイアーウォールでブロックされていないか確認してください。CageClientとの通信には TCP のポート54321 と 54323 を使います。これらのポートへのアクセスをブロックしないように設定してください。

VTC側が正常に待ち受け開始できている場合にはログに以下のメッセージが出ます。
```
LogTemp: Warning: ZSocket binding to tcp://*:54321
LogTemp: Warning: ReportSocket (tcp://*:54321) and CmdSocket (tcp://*:54323) are ready
```

何らかの理由によりいずれかのポートが使えなかった場合は例えば以下のメッセージが出ます。
```
LogTemp: Warning: ZSocket binding to tcp://*:54321
LogTemp: Error: Could not bind ReportSocket : -100 [Unknown error]
```
この場合例えば別のVTC等が起動しているなど何かのプログラムが同じポートを使用している可能性があります。該当のプロセスを終了して再度試したり、OSを再起動して試してください。

なお、ログは Unreal Editor では Output Log ウィンドウで、パッケージ版の場合 VTC.exe があるディレクトリ以下の VTC/Saved/Logs/VTC.log で確認できます。
