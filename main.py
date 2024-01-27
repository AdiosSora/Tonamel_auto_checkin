import cv2
import numpy as np
import PySimpleGUI as sg
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import urllib.request, urllib.error
import configparser


if __name__ == '__main__':
    
    # --------------------------------------------------
    # configparserの宣言とiniファイルの読み込み
    # --------------------------------------------------
    config_ini = configparser.ConfigParser()
    config_ini.read('config.ini', encoding='utf-8')

    # --------------------------------------------------
    #PySimpleGUI 設定
    # --------------------------------------------------
    layout = [
            [sg.Text('', size=(40, 1), justification='center', font='Helvetica 20',key='-status-')],
            [sg.Text('カメラ番号: ', size=(8, 1)), sg.InputText(default_text='0',  size=(4, 1),key='-camera_num-')],
            [sg.Image(filename='', key='image')],
            [sg.Button('読み取り開始', size=(12, 1), font='Helvetica 14',key ='-start-'),
                sg.Button('終了', size=(10, 1), font='Helvetica 14', key='-exit-'),  ]
            ]

    mainWindow = sg.Window('トナメル自動チェックイン',layout, location=(1200, 100)) # メインウィンドウ設定
    
    sg.theme('DarkGrey6') #テーマ設定

    # --------------------------------------------------
    # Selemium / chromeDriver 設定
    # --------------------------------------------------
    
    options = Options()
    options.binary_location = config_ini['DEFAULT']['ChromeExE']
    service = Service(config_ini['DEFAULT']['ChromeDriver'])
    driver = ''
    cookies = ''
    
    # --------------------------------------------------
    # 変数 設定
    # --------------------------------------------------
    qrd = cv2.QRCodeDetector()# QRCodeDetectorインスタンス生成
    font = cv2.FONT_HERSHEY_SIMPLEX #フォント設定
    recording = False # ビデオ読み取りフラグ
    cookieSettting = False # ログイン設定中フラグ
    prev_url = '' # 前回読み取ったQRコード
    prev_counter = 0 # 前回読み取ったQRコードを再度読み取るまでのカウンター
    prev_reset = int(config_ini['DEFAULT']['ResetCount']) # 再読み込みまでのカウンター
    tonnamel_login_urL = config_ini['DEFAULT']['TonamelUrl'] # TonamelのURL
    
    
    def checkURL(url): #URL形式チェック
        try:
            f = urllib.request.urlopen(url)
            f.close()
            return True
        except:
            return False
        
    def showImg(frame): # 画像表示
            print('画像表示')
            imgbytes = cv2.imencode('.png', frame)[1].tobytes() 
            mainWindow['image'].update(data=imgbytes)
            
    while True:
        event, values = mainWindow.read(timeout=20)
        #終了ボタン押下 システム終了
        if event in (None, '-exit-'):
            print('終了ボタン押下')
            driver.quit()
            break
        
        #読み取り開始ボタン押下 ビデオ表示開始
        elif event == '-start-':
            if recording == False:
                print('STARTボタンが押されました')
                mainWindow['-status-'].update('読み取り中...')
                camera_number = int(values['-camera_num-'])
                cap = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)
                
                
                driver = webdriver.Chrome(service=service, options=options)
                driver.get(tonnamel_login_urL)
                
                #ログインボタン押下
                driver.implicitly_wait(10)
                element = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[1]/header/div[1]/div/div[2]').click()
                #Twitterアイコン押下
                driver.implicitly_wait(10)
                element = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[1]/header/div[2]/div[2]/div/section/div[5]/div[2]/div').click()
                
                #Twitter連携ログインウィンドウへ遷移
                time.sleep(4)
                newhandles = driver.window_handles
                driver.switch_to.window(newhandles [1])
                #ログイン情報自動入力
                driver.find_element(By.XPATH,'//*[@id="username_or_email"]').send_keys(config_ini['USER_SETTING']['TonamelLoginId'])
                driver.find_element(By.XPATH,'//*[@id="password"]').send_keys(config_ini['USER_SETTING']['TonamelLoginPassword'])
                #ログイン実行
                element = driver.find_element(By.XPATH, '//*[@id="allow"]').click()
                #自動チェックイン画面へ戻る
                driver.implicitly_wait(10)
                driver.switch_to.window(newhandles [0])
                recording = True
                mainWindow['-start-'].update('読み取り中止')
                
            else:
                #STOPボタン押下 ビデオ表示終了
                print('STOPボタンが押されました')
                mainWindow['-status-'].update('')
                # 幅、高さ　戻り値Float
                W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                # print(H,W)
                img = np.full((H, W), 0)
                # ndarry to bytes
                imgbytes = cv2.imencode('.png', img)[1].tobytes()
                mainWindow['image'].update(data=imgbytes)
                cap.release()
                cv2.destroyAllWindows()
                driver.close()
                recording = False
                mainWindow['-start-'].update('読み取り開始')

        #レコーディング処理
        if recording:
            ret, frame = cap.read()
            mainWindow['-status-'].update('読み取り中...')
            print('レコーディング')
            
            #同一QRコードを読み取る制限カウンターを読み取る毎に減らす
            if(prev_counter>0):
                prev_counter -= 1
            
            if ret:
                # QRコードデコード
                retval, decoded_info, points, straight_qrcode = qrd.detectAndDecodeMulti(frame)

                if retval:
                    points = points.astype(np.int32) #QRコード座標

                    for dec_inf, point in zip(decoded_info, points):
                        print('QRコード判定')
                        if dec_inf == '':
                            continue

                        # QRコード座標取得
                        x = point[0][0]
                        y = point[0][1]

                        # QRコードデータ
                        frame = cv2.putText(frame, dec_inf, (x, y - 6), font, .3, (0, 0, 255), 1, cv2.LINE_AA)

                        # バウンディングボックス
                        frame = cv2.polylines(frame, [point], True, (0, 255, 0), 1, cv2.LINE_AA)
                        
                        #前回読み取ったQRコードは一定時間読み取らない
                        if(prev_url != dec_inf or prev_counter == 0):
                            print('QRコード読み取り成功')
                            #読み取りカウンターリセット
                            prev_counter = prev_reset
                            
                            # QRコードデータ
                            frame = cv2.putText(frame, '読み取り中', (x, y - 12), font, .3, (0, 0, 255), 1, cv2.LINE_AA)
                            showImg(frame)
                            if(checkURL(dec_inf)):
                                prev_url = dec_inf
                                driver.get(dec_inf)
                                driver.implicitly_wait(10)
                                try:
                                    element = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[1]/div[1]/div[3]/div/div/div[2]/p[1]')
                                    if element.is_enabled():
                                        element.click()
                                except NoSuchElementException:
                                    mainWindow['-status-'].update('読み取り中...チェックイン済みです。')
                            break
                showImg(frame) # 画像表示

    mainWindow.close()
    

