import json
import wx
from threading import Thread
from os import getcwd, path, remove, rename, makedirs, walk
from os.path import join ,exists ,dirname ,abspath
from subprocess import Popen, PIPE, STDOUT
from sys import argv, exit
from shutil import rmtree
from platform import  system 

class Exe_builder(wx.Frame):

    def __init__(self, *args, **kw):
        """
            Sınıfın başlatıcı metodudur. 
        """
        if system() != 'Windows':
            wx.LogError("Bu Program Sadece Windows Platformunda Çalışmaktadır")
            wx.LogError("Diğer platformlarla uyumlu değildir ve çalıştırılamaz.")
            wx.LogError("Farklı bir işletim sistemi kullanıyorsanız, bu uygulamanın çalıştırılması mümkün değildir.")
            exit()

        super(Exe_builder, self).__init__(*args, **kw)
        
        exe_dizini = dirname(abspath(__file__))
        ikon_adi = "Exe Builder.png"
        self.icon_path = join(exe_dizini,     ikon_adi)
        appdata = join(path.expanduser('~'), 'AppData', 'Local', 'Exe_builder')
        makedirs(appdata, exist_ok=True)
        self.Hata_path = join(appdata, 'Exe_builder_hata.txt')
        self.language_path = join(appdata, "language_data.json")
        self.renk_path = join(appdata, 'Renk_data.json')

        self.dil_paketi = self.dil_kontrol()

        self.SetTitle("Exe Builder")

        boyut = (300, 300)
        pozisyon = (560, 150)

        self.SetSize(boyut)
        self.SetSizeHints(*boyut)
        self.SetPosition(pozisyon)

        self.Center()
        self.SetBackgroundColour(self.renk_kontrol())

        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER)
        
        self.icon = wx.Icon(self.icon_path, wx.BITMAP_TYPE_PNG) 
        self.SetIcon(self.icon)

        self.menubar = wx.MenuBar()
        self.pencere_menü = wx.Menu()

        self.hata_kayitlari_item = self.pencere_menü.Append(-1, self.dil_paketi["hata"])
        self.Bind(wx.EVT_MENU, self.Hata_erişim_Gui, self.hata_kayitlari_item)

        self.Tema = self.pencere_menü.Append(-1, self.dil_paketi["tema"])
        self.Bind(wx.EVT_MENU, self.Tema_ayarlama, self.Tema)
        
        self.language = self.pencere_menü.Append(-1, self.dil_paketi['dil'])
        self.Bind(wx.EVT_MENU, self.dil_degistir, self.language)

        self.kapat_item = self.pencere_menü.Append(wx.ID_EXIT, self.dil_paketi['kapat'])
        self.Bind(wx.EVT_MENU, self.kapat, self.kapat_item)

        self.menubar.Append(self.pencere_menü, self.dil_paketi['menü'])
        self.SetMenuBar(self.menubar)

        self.arayüz_olustur()

    def arayüz_olustur(self):

        """
            Kullanıcı arayüzünün oluşturulduğu fonksiyon.
        """
        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.baslik_etiket = wx.StaticText(self.panel, label=self.dil_paketi['Yapılandırma'], size=(100, -1))
        self.baslik_etiket.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        vbox.Add(self.baslik_etiket, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)

        self.FileorDir = wx.ComboBox(self.panel, choices=["onedir", "onefile"],style=wx.CB_READONLY, size=(150, -1))  
        vbox.Add(self.FileorDir, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        self.FileorDir.SetToolTip(self.dil_paketi['dosya_klasor'])
        self.FileorDir.SetValue("onefile")
        
        self.Console_Window = wx.ComboBox(self.panel, choices=["windowed", "console"],style=wx.CB_READONLY, size=(150, -1))  
        vbox.Add(self.Console_Window, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        self.Console_Window.SetToolTip(self.dil_paketi['çalışma_yolu'])
        self.Console_Window.SetValue("windowed")

        self.exe_path_sec = wx.CheckBox(self.panel, label="Dizin Seçme", size=(150, -1))
        vbox.Add(self.exe_path_sec, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        self.exe_path_sec.SetToolTip(self.dil_paketi['klasor_sec'])

        self.dist_temizleme_check = wx.CheckBox(self.panel, label=self.dil_paketi['kalıntı_btn'], size=(150, -1))
        vbox.Add(self.dist_temizleme_check, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        self.dist_temizleme_check.SetToolTip(self.dil_paketi['build'])
        
        self.icon_seçme = wx.CheckBox(self.panel, label=self.dil_paketi['icon_btn'], size=(150, -1))
        vbox.Add(self.icon_seçme, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        self.icon_seçme.SetToolTip(self.dil_paketi['icon'])

        self.cıkıkayıt = wx.CheckBox(self.panel, label=self.dil_paketi['cikti_kayıt'], size=(150, -1))
        vbox.Add(self.cıkıkayıt, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        self.cıkıkayıt.SetToolTip(self.dil_paketi['çıktı_sec'])
        
        self.başlat = wx.Button(self.panel, label=self.dil_paketi['islem_baslat'], size=(100, -1))
        self.başlat.Bind(wx.EVT_BUTTON, lambda event: self.Arka_p(fonksiyon=self.main))
        self.başlat.SetToolTip(self.dil_paketi['islem_baslat'])
        self.başlat.SetBackgroundColour("Green")
        vbox.Add(self.başlat, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)

        self.panel.SetSizer(vbox)
        self.panel.Layout()
        
        self.panel.Fit()
    
    def kapat(self , event):
        exit()

    def path_seçme(self):
        """
        Dosya seçme işlemini gerçekleştiren fonksiyon.
        """        
        file_types = "Python dosyaları (*.py)|*.py|Metin dosyaları (*.txt)|*.txt"
        self.file_dialog = wx.FileDialog(self.panel, self.dil_paketi['dosya_sec'], wildcard=file_types, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        dosya_yolu = None

        if self.file_dialog.ShowModal() == wx.ID_OK:
            dosya_yolu = self.file_dialog.GetPath()
            dosya, uzanti = path.splitext(dosya_yolu)
            if uzanti.replace(".", "") == "txt":
                dosya_yolu =self.uzantı_replace(dosya_yolu)
                wx.MessageBox(self.dil_paketi['dosya_degistirildi'], "Bilgi", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.LogError(self.dil_paketi['klasor_secilmedi'])
        
        return dosya_yolu 
    
    def uzantı_replace(self, yol):
        """
        Dosya uzantısını değiştiren fonksiyon.
        """
        dosya_adi, uzanti = path.splitext(yol)
        yeni_yol = dosya_adi + ".py"
        rename(yol, yeni_yol)
        return yeni_yol


    def Arka_p(self, fonksiyon, *args):
        thread = Thread(target=fonksiyon, args=args)
        thread.daemon = True
        thread.start()

    def hata_kayit(self, hata_mesaji):
        try:
            with open(self.Hata_path, "a", encoding="utf-8") as dosya:
                dosya.write("\n" + hata_mesaji + "\n")
                wx.LogError(hata_mesaji)
        except Exception as e:
            wx.LogError(f"{self.dil_paketi['hata_kaydi_hata']}: {e}")

    def durum(self , durum= None):
        if durum:
            self.başlat.SetLabel(self.dil_paketi['islem_baslat'])
            self.başlat.SetBackgroundColour("red")
            self.başlat.Enable(False)
        else :
            self.başlat.SetLabel(self.dil_paketi['islem_yurutuluyor'])
            self.başlat.Enable(True)
            self.başlat.SetBackgroundColour("Green")

    def kalıntı_temizleme(self):
        try:
            rmtree(path.join(path.dirname(path.abspath(argv[0])), "build"))
            mevcut_dizin = getcwd()
            for kök, _, dosyalar in walk(mevcut_dizin):
                for dosya in dosyalar:
                    if dosya.endswith(".spec"):
                        dosya_yolu = path.join(kök, dosya)
                        remove(dosya_yolu)
            wx.MessageBox(self.dil_paketi['kalinti_temizleme_basarili'], 'Bilgi', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            self.hata_kayit(self.dil_paketi['kalinti_temizleme_hata'] + str(e))

    def yapılandırma(self):

        def Exe_path_fuc(event):
            """
            Kullanıcının bir klasör seçmesini sağlar ve seçilen klasör yolunu döndürür.
            """
            if self.exe_path_sec.GetValue():
                Expo = wx.DirDialog(None, self.dil_paketi['klasor_sec'])
                if Expo.ShowModal() == wx.ID_OK:
                    klasor_yolu = Expo.GetPath()
                    wx.MessageBox(self.dil_paketi['klasor_degistirildi'],"Bilgi" , wx.OK | wx.ICON_INFORMATION)
                    return klasor_yolu
                else:
                    wx.LogError(self.dil_paketi['klasor_secilmedi'])
                    klasor_yolu = getcwd()
                    return klasor_yolu
            else:
                return getcwd() 
            
        def icon_secme_fuc():
            icon_durum = False
            icon_dosya_yolu = ""
            if self.icon_seçme.GetValue():
                icon_durum = True
                file_types = "İcon dosyaları (*.ico)|*.ico|Resim dosyaları (*.png)|*.png"
                file_dialog = wx.FileDialog(self.panel, self.dil_paketi['dosya_sec'], wildcard=file_types, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
                
                if file_dialog.ShowModal() == wx.ID_OK:
                    icon_dosya_yolu = file_dialog.GetPath()    
                else:
                    wx.LogError(self.dil_paketi['dosya_secilmedi'])
                    icon_durum = False
            return icon_durum, icon_dosya_yolu

        exe_path = Exe_path_fuc("")
        icon_durum,icon_dosya_yolu=icon_secme_fuc()

        if  icon_durum == True:
            command = [
                    "pyinstaller",
                    "--noconfirm",
                    f"--{self.FileorDir.GetValue()}",
                    f"--{self.Console_Window.GetValue()}",
                    f"--icon={icon_dosya_yolu}",
                        self.path,
                    "--distpath",
                    f"{exe_path}"]
                
            return command
        
        else :
            command = [
                "pyinstaller",
                "--noconfirm",
                f"--{self.FileorDir.GetValue()}",
                f"--{self.Console_Window.GetValue()}",
                    self.path,
                "--distpath",
                f"{exe_path}"]
            
            return command
        
    def main(self):
        """
        Ana işlem fonksiyonu.
        """
        try:
            self.path =self.path_seçme()
            command = self.yapılandırma()
            self.durum(durum=True)
            process = Popen(command, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
            out, err = process.communicate()                
            if process.returncode != 0:
                self.hata_kayit(hata_mesaji=f"{self.dil_paketi['islem_sirinda_hata']}:\n{err}")
            else:
                if self.dist_temizleme_check.GetValue() == 1:
                    self.kalıntı_temizleme()
                if self.cıkıkayıt.GetValue() == 1:
                    self.İşlem_Kaydı(out)
                wx.MessageBox(self.dil_paketi['islem_tamamlandı'], 'Bilgi', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            self.hata_kayit(hata_mesaji=f"{self.dil_paketi['islem_sirinda_hata']}:\n{e}")
        finally : 
            self.durum(durum=False)

    def Hata_erişim_Gui(self, event):
        """
            Uygulama Hatalarını grafik arayüzde göstermek için kullanılan fonksiyon.
        """
        try:
            with open(self.Hata_path, "r+", encoding="utf-8") as hatalar:
                kayıtlar = hatalar.read()
                if not kayıtlar:
                    hatalar.write(" ")
                    hatalar.seek(0)
                    kayıtlar = hatalar.read()
                Toplam_hata = str((len(kayıtlar.split("\n")) / 2).__round__()) + "\n\n"

            hata_erisim_frame = wx.Frame(None, title=f"{self.dil_paketi['kalan_hata_kaydi']} : {Toplam_hata}", size=(600, 400))
            panel = wx.Panel(hata_erisim_frame)
            sizer = wx.BoxSizer(wx.VERTICAL)

            text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
            text_ctrl.SetValue(kayıtlar)
            sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)

            icon = wx.Icon(self.icon_path, wx.BITMAP_TYPE_PNG) 
            hata_erisim_frame.SetIcon(self.icon)

            panel.SetSizer(sizer)
            hata_erisim_frame.Show()

        except Exception as e:
            self.hata_kayit(f"Hata: {e}")
            return
        
    def İşlem_Kaydı(self, Çıktı):
        """
        İşlem çıktısını kaydeden fonksiyon.
        """
        try:
            Expo = wx.DirDialog(None, self.dil_paketi["cikti_kayıt"])
            if Expo.ShowModal() == wx.ID_OK:
                klasor_yolu = Expo.GetPath()
                dosya_yolu = join(klasor_yolu, "İşlem Kaydı.txt")
                with open(dosya_yolu, "w", encoding="utf-8") as dosya:
                    dosya.write(f"{Çıktı}\n")
            else:
                wx.LogError(self.dil_paketi['cikti_kayit_uyari'])
        except Exception as e:
            self.hata_kayit(hata_mesaji=f"{self.dil_paketi['disa_aktarma_hata']}:\n{e}")

    def jsona_yaz(self, veri ,tur):
        """
        Belirtilen dosyaya JSON formatında verilen veriyi yazan fonksiyon.
        """
        if tur == "renk" :
                
            with open(self.renk_path, 'w' ,encoding="utf-8") as json_dosyasi:
                json.dump(veri, json_dosyasi, indent=4)
        if tur == "dil" :
            with open(self.language_path, 'w' ,encoding="utf-8") as json_dosyasi:
                json.dump(veri, json_dosyasi, indent=4)

    def Tema_ayarlama(self, event):
        """
            Tema değiştirmek için kullanılan fonksiyon.
        """
        renk = wx.ColourDialog(self)
        if renk.ShowModal() == wx.ID_OK:
            sa = renk.GetColourData().GetColour()
            json_veri ={
                            "renk": '#{:02x}{:02x}{:02x}'.format(*sa[:3])
                        }
            self.jsona_yaz(json_veri, tur = "renk")
            self.SetBackgroundColour(sa)
            self.Refresh(True)

        renk.Destroy()

    def dil_degistir(self, event):
        """
            Dil değiştirmek için kullanılan fonksiyon.
        """
        dil_secenekleri = {'İngilizce': 'English', 'Türkçe': 'Turkish'}
        secilen_dil = wx.GetSingleChoice(self.dil_paketi['dil_secimi'], 'Dil Seçimi', list(dil_secenekleri.keys()))
        if secilen_dil:
            json_veri ={
                    "Dil": dil_secenekleri[secilen_dil]
                    }
            self.jsona_yaz(json_veri, tur = "dil")
            wx.MessageBox(self.dil_paketi['dil_degistirme_basarili'],
                        'Bilgi', wx.OK | wx.ICON_INFORMATION)
            self.kapat("")

    def renk_kontrol(self):
        """
        Belirtilen JSON formatındaki veriyi okuyup Renk ayarlarını günceller
        """
        if exists(self.renk_path):
            with open(self.renk_path, "r" ,encoding="utf-8") as dosya:
                json_icerik = json.load(dosya)
                renk_degeri = json_icerik["renk"]
            return renk_degeri 
        else: 
            return "#f0f8ff"
            
    def dil_kontrol(self):
        """
        Belirtilen JSON formatındaki veriyi okuyup Dil ayarlarını günceller
        """
        tr = {
            # Genel İşlemler
            "menü": "Menü",
            "tema": "Temayı Değiştir",
            "dil": "Dili Değiştir",
            "kapat": "Kapat",
            "Yapılandırma": "Yapılandırma",

            # Çalışma Yolu
            "çalışma_yolu": "Çalışma Yolunu Seç, Konsol yada Pencere",
            "dosya_klasor": "Tek Klasör Yada Tek Dosya...",

            # Temizleme İşlemi
            "build": "Build Klasörü ve .Spec Dosyalarını Temizle.",
            "kalıntı_btn": "Gereksiz Dosyaları Temizle",

            # İkon Seçimi
            "icon": "Uygulamanız İçin İkon Seçmek için Seçin.",
            "icon_btn": "İkon Seçme",

            # Çıkış
            "çıktı_sec": "Yapılan İşlemin Çıktısını Kaydetmek için Seçin.",

            # Hata İşlemleri
            "hata": "Hata Kayıtları",
            "hata_mesaji": "Hata Mesajı:",
            "hata_kaydi_hata": "Hata Kaydı Sırasında Bir Hata Oluştu:",
            "hata_kaydi_olusturuldu": "Hata Kaydı Oluşturuldu.",
            "islem_sirinda_hata": "İşlem Sırasında Bir Hata Oluştu:",

            # Dosya ve Klasör Seçimi
            "dosya_sec": "Dosya Seç",
            "dosya_secme": "Dosya Seçme",
            "dosya_secilmedi": "Dosya Seçilmediği İçin İşlem İptal Edildi.",
            "dosya_degistirildi": "Txt Dosya Uzantısı py Olarak Değiştirildi.",
            "klasor_sec": "İşlem Dizini Seç",
            "klasor_degistirildi": "İşlem Dizini Değiştirildi.",
            "klasor_secilmedi": "İşlem Dizini Seçilmediği İçin İşlem İptal Edildi.",

            # İşlem Yolu ve Çıktı
            "islem_yolu": "İşlem Yolu",
            "cikti_kayıt": "Çıktı Kayıt İçin Klasör Seç",
            "cikti_kayit_uyari": "Klasör Seçilmedi. Dışa Aktarma İşlemi İptal Edildi.",

            # Dil Seçimi
            "dil_secimi": "Lütfen Bir Dil Seçin / Please Select a Language",
            "dil_degistirme_basarili": "Dil Değiştirme İşlemi Başarıyla Gerçekleştirildi. Uygulamayı Yeniden Başlatmanız Gerekebilir.",

            # Hata ve Kalıntı Bilgileri
            "kalan_hata_kaydi": "Toplam Hata Kaydı",
            "hata_icerik": "Hata İçeriği:",
            "kalan_hata": "Kalan Hata:",
            "islem_tamamlandi": "İşlem Tamamlandı.",
            "kalinti_temizleme_basarili": "Kalıntılar Temizlendi.",
            "kalinti_temizleme_hata": "Kalıntılar Temizlenirken Bir Hata Oluştu:",

            # Dışa Aktarma
            "disa_aktarma_basarili": "Dışa Aktarma İşlemi Başarıyla Tamamlandı.",
            "disa_aktarma_hata": "Dışa Aktarma İşlemi Sırasında Bir Hata Oluştu:",

            # İşlem Başlatma ve Durum
            "islem_baslat": "İşlemi Başlat",
            "islem_yurutuluyor": "İşlem Devam Ediyor...",
        }

        en = {
            # Genel İşlemler
            "menü": "Menu",
            "tema": "Change Theme",
            "dil": "Change Language",
            "kapat": "Close",
            "Yapılandırma": "Configuration",

            # Çalışma Yolu
            "çalışma_yolu": "Console or Window",
            "dosya_klasor": "File or Folder",

            # İşlem Başlatma ve Durum
            "islem_baslat": "Start Operation",
            "islem_yurutuluyor": "Operation in Progress...",

            # Temizleme İşlemi
            "build": "Clean Build Folder and .Spec Files.",
            "kalıntı_btn": "Clean Junk Files",

            # İkon Seçimi
            "icon": "Select to Choose Icon for Your Application",
            "icon_btn": "Select Icon",

            # Çıkış
            "çıktı_sec": "Select to Save the Output of the Operation Performed.",

            # Hata İşlemleri
            "hata": "Error Logs",
            "hata_mesaji": "Error Message:",
            "hata_kaydi_hata": "An Error Occurred While Creating Error Logs:",
            "hata_kaydi_olusturuldu": "Error Log Created.",
            "islem_sirinda_hata": "An Error Occurred During the Operation:",

            # Dosya ve Klasör Seçimi
            "dosya_sec": "Select File",
            "dosya_secme": "File Selection",
            "dosya_secilmedi": "File Not Selected, Operation Cancelled.",
            "dosya_degistirildi": "Txt File Extension Changed to Py.",
            "klasor_sec": "Select Directory",
            "klasor_degistirildi": "Directory Changed",
            "klasor_secilmedi": "Directory Not Selected, Operation Cancelled.",

            # İşlem Yolu ve Çıktı
            "islem_yolu": "Operation Path",
            "cikti_kayıt": "Select Folder for Output",
            "cikti_kayit_uyari": "Folder Not Selected. Export Operation Cancelled.",

            # Dil Seçimi
            "dil_secimi": "Please Select a Language.",
            "dil_degistirme_basarili": "Language Changed Successfully. You May Need to Restart the Application.",

            # Hata ve Kalıntı Bilgileri
            "kalan_hata_kaydi": "Total Error Logs:",
            "hata_icerik": "Error Content:",
            "kalan_hata": "Remaining Errors:",
            "islem_tamamlandi": "Operation Completed.",
            "kalinti_temizleme_basarili": "Residue Cleared.",
            "kalinti_temizleme_hata": "An Error Occurred While Cleaning the Residues:",

            # Dışa Aktarma
            "disa_aktarma_basarili": "Export Operation Completed Successfully.",
            "disa_aktarma_hata": "An Error Occurred During the Export Operation:",
            "islem_sirinda_hata": "An error occurred during the operation:"}
        
        
        if exists(self.language_path):
            with open(self.language_path, "r" ,encoding="utf-8") as dosya:
                veri = json.load(dosya)
                dil = veri["Dil"]
                if dil == "English":
                    return en
                else :
                    return tr
        else: 
            return tr

if __name__ == '__main__':
    app = wx.App(False)
    frame = Exe_builder(None)
    frame.Show(True)
    app.MainLoop()
