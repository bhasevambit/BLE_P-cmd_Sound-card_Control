from pybleno import *
import signal
# Pコマンド(BLE Write )向けCharacteristicモジュールの全クラスをインポート
from P_Characteristic import *
# Sコマンド(BLE Notify)向けCharacteristicモジュールの全クラスをインポート
from S_Characteristic import *

# --- No generate bytecode cache ---
import sys
sys.dont_write_bytecode = True
# ----------------------------------


# BLE通信 各種設定値
SERVICE_NAME = 'BLE_TEST'
SERVICE_UUID = 'cdf7b788-df74-4a8e-86df-209297d273ee'
# Sコマンド(BLE Notify)向けCharacteristic UUIDの設定
S_COMMAND_CHARACTERISTIC_UUID = 'f0542e2b-9288-4675-9498-8a1d95cccc80'
# Pコマンド(BLE Write )向けCharacteristic UUIDの設定
P_COMMAND_CHARACTERISTIC_UUID = '7bf9252c-3ed7-4d9e-9c00-83b256e9f04e'


print('==========================================')
print('=== BLE-TEST by pyBleno ===')
print('==========================================')
print('')
print('BLE Notify and Write TEST START ...>>>')
print('')


def onStateChange(state):
    print('on -> stateChange: ' + state)

    if (state == 'poweredOn'):
        bleno.startAdvertising(name=SERVICE_NAME, service_uuids=[SERVICE_UUID])
    else:
        bleno.stopAdvertising()


def onAdvertisingStart(error):
    print('on -> advertisingStart: ' +
          ('error ' + error if error else 'success'))

    if not error:
        bleno.setServices([
            BlenoPrimaryService({
                'uuid': SERVICE_UUID,
                'characteristics': [
                    # S_Characteristicモジュール内のS_Characteristicクラスから生成したインスタンスオブジェクト(=characteristicsクラスを継承)
                    s_Characteristic,
                    # P_Characteristicモジュール内のP_Characteristicクラスから生成したインスタンスオブジェクト(=characteristicsクラスを継承)
                    p_Characteristic
                ]
            })
        ])


# --- Notifyタスク関数 ---
def notify_task():
    global facing_azimuth

    # facing_azimuthを0～359(360度を1度刻み)でインクリメントループ
    # **** このfacing_azimuth値が、9軸センサ部から渡されるデバイス方位角値にあたる。後々この変数で9軸センサ部から値受取りを行うイメージ ****
    if facing_azimuth < 359:
        facing_azimuth += 1
    else:
        facing_azimuth = 0

    # S_Characteristicインスタンスオブジェクトの"._value" facing_azimuth値をセット
    s_Characteristic._value = facing_azimuth
    if s_Characteristic._updateValueCallback:

        # Notifyデータの標準出力表示(for Terminal Monitering)
        print('Sending notification with value : ' +
              str(s_Characteristic._value))

        notificationBytes = str(s_Characteristic._value).encode()
        s_Characteristic._updateValueCallback(
            data=notificationBytes)  # Notifyによる値の発出


# ================
# === main処理 ===
# ================
if __name__ == '__main__':
    bleno = Bleno()  # pyblenoモジュール内のBlenoクラスからインスタンスオブジェクト(=bleno)を生成
    # S_Characteristicモジュール内のS_Characteristicクラスからインスタンスオブジェクト(=s_Characteristic)を生成
    s_Characteristic = S_Characteristic(S_COMMAND_CHARACTERISTIC_UUID)
    # P_Characteristicモジュール内のP_Characteristicクラスからインスタンスオブジェクト(=p_Characteristic)を生成
    p_Characteristic = P_Characteristic(P_COMMAND_CHARACTERISTIC_UUID)

    bleno.on('stateChange', onStateChange)  # BLE onState開始準備
    bleno.on('advertisingStart', onAdvertisingStart)  # BLE Advertise開始準備

    bleno.start()  # BLE処理開始

    # 0.2秒周期のNotify通知の実装
    import time  # 0.2秒ウェイト向けのtimeライブラリのインポート
    # notify_task向けのカウンタ変数(関数外でも共有するため、notify_task関数内でglobal変数定義済)
    facing_azimuth = 0

    while True:
        notify_task()  # Notifyタスク関数の実行
        time.sleep(0.2)  # 0.2秒のウェイト
