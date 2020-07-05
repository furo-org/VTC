# VTC: Virtual Tsukuba Challenge

つくばチャレンジ 3rd stage の確認走行区間を模擬した環境と、そこで動作する移動ロボットシミュレータ。
[![VTC with lidar intensity enabled](docs/ScreenShot-i.png)](https://www.youtube.com/watch?v=gb9t7RFmgpc)

## 関連Repository

+ [Cage Plugin](https://github.com/furo-org/CagePlugin): 移動ロボット、センサ等の機能をパッケージしたプラグイン
+ [ZMQUE Plugin](https://github.com/furo-org/ZMQUE): ZeroMQのdllをロードするプラグイン
+ [PxArticulationLink Plugin](https://github.com/yosagi/PxArticulationLink): PhysX Articulation APIにアクセスするためのプラグイン
+ [cage-clientライブラリ](https://github.com/furo-org/CageClient): シミュレータ内ロボットと通信し、コマンドを送りステータスを取得するライブラリ

## 動作環境

以下の環境で動作確認しています。

PC

+ Ryzen7 1800X(3.6GHz) + GeForce GTX 1080
+ Core i7 7700HQ(2.8GHz) + GeForce GTX 1060

ソフトウェア環境

+ Windows 10 1909 64bit
+ Visual Studio 2019 16.5.4
+ Unreal Engine 4.25.1

## ドキュメント

+ [シミュレータの操作方法](docs/runtime.md)
+ [エディタでの開発環境設定](docs/editor.md)

環境を編集したり、シミュレータのコードに手を入れるにはエディタでの開発環境をセットアップする必要があります。既存の環境でロボットを走らせるだけならばパッケージ済みバイナリと[cage-clientライブラリ](https://github.com/furo-org/CageClient)があれば十分です。

## パッケージ済みバイナリのダウンロード

+ [VTC 2020/5/28版 Windows 64bit 約1GB](https://1drv.ms/u/s!AkekAlL4McuXlQOBSBVlSNaRIZpQ?e=veg3e0)
+ [VTC2019 Windows 64bit 約750MB](https://chibakoudai-my.sharepoint.com/:u:/g/personal/yoshida_tomoaki_p_chibakoudai_jp/ETDQWwohngxKsu09_ga2H9UBs5A4OmVFnmzQckcgW8upzA?e=IJuMfI)
+ [VTC2018 (以前のバージョン) Windows 64bit 約700MB](https://chibakoudai-my.sharepoint.com/:u:/g/personal/yoshida_tomoaki_p_chibakoudai_jp/ER00YHh9YYFEpBnFCl16Ug4BnmRve_PuS1y1sB2-dvryDw?e=cxDaMb)

zipを展開してVTC.exe(もしくは古いものはVTC2018.exe)を起動するだけですので各種アカウントの用意やインストールなどをせずに手軽に試せます。全画面とウィンドウモードの切り替えはAlt-Enterで、終了はAlt-F4もしくはEscです。パッケージ版はUnreal Editorで編集することはできませんが[cage-clientライブラリ](https://github.com/furo-org/CageClient)を使ってコマンドを送ることでロボットを動かすことができますし、lidarのシミュレーションも動きます。

## 環境データについて

環境の構築に国土地理院基盤地図情報(基盤地図情報 基本項目及び数値標高モデル(5mメッシュ) 544000,544010)を承認を受けて使用しています。

「測量法に基づく国土地理院長承認（使用）R 2JHs 231」

以下のファイルは基盤地図情報 基本項目をベースに加工して生成したものです。
 + Assets/TC-Asphalt-geo.tif
 + Assets/TC-Pedestrian-geo.tif
 + Assets/TC-Park-Green-geo.tif
 + Assets/TC-Water-geo.tif
 + Assets/TC-Buildings-geo.tif

さらに以下のファイルはこれらファイルからVTCのLandscape Layerに適用できる形にAssets/LayerGen.pyを使って加工したものです

+ Assets/Layer-Asphalt.png
+ Assets/Layer-Park-Green.png
+ Assets/Layer-Pedestrian.png
+ Assets/Layer-Water.png

また、Assets/TC-DEM-geo.tifは数値標高モデル(5mメッシュ)を使って生成したファイルで、Assets/heightmap.png はこれをVTCのLandscape heightmapに適用できる形にAssets/LandscapeGen.pyを使って加工したものです。
これらファイルの二次利用したい場合はその他ファイル群とは条件が異なりますので注意してください。

## License

VTCはApache2.0とします。

Copyright [2017-2020] Tomoaki Yoshida <yoshida@furo.org>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
