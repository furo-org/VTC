# VTC2018

つくばチャレンジ2018の確認走行区間を模擬した環境。
![Screen Shot](ScreenShot.png)

## 動作環境

以下の環境で動作確認しています。

+ Windows 10 1809 64bit
+ Visual Studio 2017 15.9.4
+ Unreal Engine 4.21.2

## 事前に必要な物

WindowsでUE4開発をするのに必要な物一式が必要です。

+ EPICGamesのアカウントとUnrealEngine4
+ EPICGamesにリンクした Githubアカウント
+ WindowsでのUE4開発環境(VS2017, UnrealEngine4, その他)
+ Windowsでのgithubにアクセスする手段
+ 50GB程のストレージ

### アカウントの準備

1. まず最初にgithubのアカウントをまだ持っていなければ、(A)[githubのページ](https://github.com)でgithubアカウントを作成します。
2. 次に[UnrealEngineのページ](https://www.unrealengine.com/ja/feed)に行き、(B)EpicGamesのアカウントを作成し、(C)ゲームデベロッパーのEULAに同意し、(D)UnrealEngineをダウンロード/インストールします。
3. さらに[Unreal Engineの接続済みアカウントのページ](https://www.unrealengine.com/account/connected)で(E)Githubアカウントと接続します。
4. その後[GithubのEpicGamesのページ](https://github.com/EpicGames)に行き、(F)InvitationをAcceptします。

上記(A)から(F)までうまくいけば、[Unreal Engineのソースコードリポジトリ](https://github.com/EpicGames/UnrealEngine)にアクセスできるようになります。


参考リンク

+ [GitHub アカウントと Epic Games アカウントの紐付けの認証プロセスのアップデート](https://www.unrealengine.com/ja/blog/updated-authentication-process-for-connecting-epic-github-accounts)
+ [アンリアル エンジンのインストール方法](http://api.unrealengine.com/JPN/GettingStarted/Installation/index.html)
+ [Installing Unreal Engine](https://docs.unrealengine.com/en-US/GettingStarted/Installation)
+ [GITHUB 経由でアンリアル・エンジン 4 C++ ソースコードにアクセスする方法](https://www.unrealengine.com/ja/ue4-on-github)

### 動作環境の準備

1. [Visual Studio 2017](https://docs.microsoft.com/en-us/visualstudio/productinfo/vs2017-system-requirements-vs)をダウンロードしてインストールします。既にインストールされている場合は、念のためVisual Studio Installerを起動し、最新のVisual Studio 2017に更新しておきます。
2. git ([Git for windows](https://gitforwindows.org))をインストールします。コマンドラインのgitが使えるようになっているほうが良いです。

### Unreal Engineのインストール

アカウントの準備(D)ではEpic Games Launcherがインストールされます。実際に使うUnreal Engineのバイナリは別途手順が必要です。

1. Epic Games Launcherを起動し、左のタブからUnreal Engineを選択。
2. 上のタブからライブラリを選択
3. Engineバージョンの右の+をクリックしてEngineスロットを追加。
4. 追加されたスロットのバージョン番号の右にある▼をクリックし、4.21.0を選択。
5. インストールをクリック。

このドキュメント執筆時点で最新のUE4は4.22ですが、動作確認しているのは4.21ですので、同じバージョンを使ってください。なお、Engineのバイナリは約10GB程あり、ダウンロードにはそこそこ時間がかかります。

### 補足

これらの他、外部プログラムからロボットを動かすには[cage-clientライブラリ](https://github.com/furo-org/cage-client)があると便利です。cage-clientは今のところLinuxで動作するのでこれを動かす環境(実機, WSL, 仮想マシンなど)が必要です。

## セットアップ

以下の手順で進めてください。

1. このリポジトリをclone
2. Plugin の submodule を更新
3. 外部アセットの追加
4. ビルドおよび起動

### クローン

%USERPROFILE%\Documents\Unreal Projects の下にクローンするとトラブルが減るかもしれません。

```
cd %USERPROFILE%"\Documents\Unreal Projects"
git clone https://github.com/furo-org/VTC2018.git
```

### Pluginのsubmoduleを更新

update_submodule.batを実行してください。もしくは以下のコマンドでも同等です。

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

これらアセットも合計で25GB程あるので、ダウンロードに時間がかかります。

### ビルドおよび起動

VTC2018.uprojectをダブルクリックすると必要なモジュールのビルドが走り、成功するとUnreal Editorが起動します。Visual Studioでソースを参照/編集するにはVTC2018.uprojectを右クリックして'Generate Visual Studio project files'すると、VTC2018.slnが生成されるので、そこから起動できます。
初回の起動時に色々生成するのでPCのスペックによっては非常に時間がかかる可能性があります。気長に待ってください。

なお、PxArticulationLink Pluginには今のところバイナリしか置いていません。リビルドしたりクリーンしたりすると必要なファイルまで消えてビルドできなくなります。その場合Plugins/PxArticulationLinkをcheckoutするなどして元に戻せば再度ビルドできるようになります。

## 使う

Unreal EditorでAlt-Pを押すとシミュレーションが始まります
シミュレーション内ではマネキンを操作して世界に干渉するか、Editorの機能で干渉することができます。マネキンの主要な操作は以下の通りです。

|キー|機能|
----|----
|w/s/a/d|前後左右|
|ctrl|走る|
|space|ジャンプ|
|f|追跡|
|g|つかむ/はなす|
|F8|マネキンから離脱|

Unreal Editorの初期設定では、Editorがフォーカスを失うとCPU使用率を下げてしまい、フレームレートが落ちます。この挙動をさけるにはメニューバー>Edit>Editor Preferences>General>Performance で Use Less CPU when in Background のチェックを外してください。

