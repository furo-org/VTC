# シミュレータの操作

## 使う

パッケージ版のバイナリを実行するか、Unreal EditorでツールバーのPlayボタン(ショートカットAlt-P)を押すとシミュレーションが始まります。
シミュレーション内ではマネキンを操作して世界に干渉するか、Unreal Editorの機能で干渉することができます。マネキンの主要な操作は以下の通りです。

|キー|機能|
----|----
|w/s/a/d|前後左右|
|ctrl|走る|
|space|ジャンプ|
|f|ロボットを追跡|
|g|つかむ/はなす|
|@|コンソール呼び出し|
|F8|マネキンから離脱 (Unreal Editorで動かした場合のみ)|
|ESC|終了(一部のバージョン)|

### コンソール変数

実行中に挙動を変更するための以下の変数があります。

|変数名|機能|
----|----
|cage.lidar.visualize|Lidar反射点の描画頻度を指定する。0で描画しない。1で全点描画、5(デフォルト)で5点に1回描画する|
|cage.lidar.broadcast|ロボットが外部から操作されていないときにlidarのパケットをbroadcastするか指定する。0(デフォルト)でbroadcastしない。1でbroadcastする。|
|cage.lidar.AirAbsorb|Lidarの大気減衰係数を設定する。デフォルトは0.001。大きくすると遠方の反射点が暗くなり、見えにくくなる。|

コンソール変数を設定するには"@"キーを押してコンソールを呼び出し(画面下に黒いバーとプロンプトが出る)、スペース区切りで変数名と設定値を入力します。変数名はTAB補間ができます。

デフォルトでは起動直後はlidarのパケットをbroadcastしないので、シミュレータを単独で動かしてlidarのパケットを覗いてみたいようなときには cage.lidar.broadcastを1にして使ってください。

### 動作確認 (スキャナ)

シミュレータ動作中に、[VeloView](https://www.paraview.org/veloview/)等のVelodyneのスキャンを可視化するツールを起動し、点群が表示されることを確認して下さい。VeloviewではVLP-16として受信してください。
なお、シミュレータは以下の手順で cage.lidar.broadcast コンソール変数を1に設定しておく必要があります。

1. @キーでコンソールを呼びだす (画面の下端にプロンプト '>' が表示される)
2. cage.lidar.broadcast 1 とタイプ(補間候補から選んでもよい)し、Enter

これでブロードキャストアドレスにlidarのUDPパケットが送信され、可視化ツールに届きます。

![VeloView](VeloView.png)

可視化できない場合は以下を確認してください。

1. 可視化ツールが別PCで動作している場合、ファイアーウォールがパケットを落としていないか
2. CageClientでシミュレータに接続して台車を操作しているプログラムがないか。台車が外部から操作されている場合は、lidarのパケットはコマンド送信元にしか送られません。


### 動作確認 (通信)

[cage-clientライブラリ](https://github.com/furo-org/CageClient) を使って通信してみます。一番手軽なのは [sampleSubscriber.py](https://github.com/furo-org/CageClient/blob/master/sampleSubscriber.py) あたりでしょう。このサンプルはpyzmqでUnrealEngineと通信し、Puffinの状態をコンソールに出力します。

pythonが動き、pyzmqがインストールされている環境でsampleSubscriber.pyを起動します。Unreal Editorが起動しているPCと同じPCで動かす場合にはコマンドラインオプションは不要です。別のPCで起動する場合にはUnreal Editorが動いているPCのIPアドレスを渡してください。うまくいけば以下のような情報が流れます。

```
$ python sampleSubscriber.py [IPアドレス]
{
"Report": {
"Name": "PuffinBP_2",
"Time": 40.707527,
"Data": {
    "Position": {
        "X": 24925.876953125,
        "Y": 15119.17578125,
        "Z": 94.71395111083985
    },
    "Pose": {
        "X": 0.003285798244178295,
        "Y": -0.003456566948443651,
        "Z": 0.0883670523762703,
        "W": 0.9960765242576599
    },
    "AngVel": {
        "X": -0.002657068893313408,
        "Y": -0.10393170267343521,
        "Z": 0.6329377293586731
    },
    "Accel": {
        "X": 6.723383903503418,
        "Y": 2.596554756164551,
        "Z": 983.0648193359375
    },
    "Yaw": 10.138204574584961,
    "LeftRpm": 0.10816722363233566,
    "RightRpm": 3.8788769245147707
}
}
}
```

プログラムからロボットを動かすには[cage-clientライブラリ](https://github.com/furo-org/CageClient)や、[cage_ros_stack](https://github.com/furo-org/cage_ros_stack)を参照してください。
