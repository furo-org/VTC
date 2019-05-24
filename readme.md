# VTC2018

つくばチャレンジ2018の確認走行区間を模擬した環境。

## 事前に必要な物

WindowsでUE4開発をするのに必要な物一式が必要です。

1. EPICGamesのアカウントとUnrealEngine4
2. EPICGamesにリンクした Githubアカウント
3. WindowsでのUE4開発環境(VS2017, UnrealEngine4, その他)
4. Windowsでのgithubにアクセスする手段

参考リンク

+ [アンリアル エンジンのインストール方法](http://api.unrealengine.com/JPN/GettingStarted/Installation/index.html)
+ [Installing Unreal Engine](https://docs.unrealengine.com/en-US/GettingStarted/Installation)
+ [GITHUB 経由でアンリアル・エンジン 4 C++ ソースコードにアクセスする方法](https://www.unrealengine.com/ja/ue4-on-github)

GithubからUE4のソースコードをCloneしてくる必要はありませんが、EULAに同意して[Unreal Engineのリポジトリ](https://github.com/EpicGames/UnrealEngine)にアクセスできるようになっている必要があります。

これらの他、外部プログラムからロボットを動かすには[cage-clientライブラリ](https://github.com/furo-org/cage-client)があると便利です。cage-clientは今のところLinuxで動作するのでこれを動かす環境(実機, WSL, 仮想マシンなど)が必要です。

## 動作環境

以下の環境で動作確認しています。

+ Windows 10 1809 64bit
+ Visual Studio 2017 15.9.4
+ Unreal Engine 4.21.2

## セットアップ

以下の手順が必要です。

1. このリポジトリをclone
2. Plugin の submodule を更新
3. 外部アセットをmigrate
4. ビルド

### クローン

%USERPROFILE%\Documents\Unreal Project の下にクローンするとトラブルが減るかもしれません。

```
cd %USERPROFILE%"\Documents\Unreal Projects"
git clone https://github.com/furo-org/VTC2018.git
```

### submoduleの更新

```
cd VTC2018
git submodule update --init --recursive --depth=1
```

これで以下のPluginが取り込まれます。
+ [Cage Plugin](https://github.com/furo-org/CagePlugin)
+ [ZMQUE Plugin](https://github.com/furo-org/ZMQUE)
+ [PxArticulationLink Plugin](https://github.com/yosagi/PxArticulationLink)

(PxArticulationLinkはUnrealEngine Repositoryのフォークなので、'--depth=1'をつけないと大量の不要なオブジェクトをダウンロードしてしまいます。)

### 外部アセットの追加

以下のアセットを一部利用しているので、Epic Games Launcherでこれらをプロジェクトに追加します。

+ [Infinity Blade: Grass lands](https://www.unrealengine.com/marketplace/ja/slug/infinity-blade-plain-lands)

+ [Paragon: Agora と Monolith の背景](https://www.unrealengine.com/marketplace/ja/slug/paragon-agora-and-monolith-environment)

+ [Open World Demo Collection](https://www.unrealengine.com/marketplace/ja/slug/open-world-demo-collection)

具体的には以下の手順を行います。

1. Epic Games Launcherを起動し、Unreal Engine のマーケットプレイスでこれらアセットを"購入"する。もしくは上記リンクから"サインインして購入"する。(購入と表記されますがどれも無料アセットです)
2. Epic Games Launcherを起動し、Unreal Engine のライブラリにある上記アセットを”プロジェクトに追加"する。

### ビルドおよび起動

VTC2018.uprojectをダブルクリックすると必要なモジュールのビルドが走り、成功するとUnreal Editorが起動します。Visual Studioでソースを参照/編集するにはVTC2018.uprojectを右クリックして'Generate Visual Studio project files'すると、VTC2018.slnが生成されるので、そこから起動できます。

なお、PxArticulationLink Pluginには今のところバイナリしか置いていません。リビルドしたりクリーンしたりすると必要なファイルまで消えてビルドできなくなります。その場合Plugins/PxArticulationLinkをcheckoutするなどして元に戻せば再度ビルドできるようになるはずです。
