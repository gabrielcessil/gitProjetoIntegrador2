import PySimpleGUI as psg
import VolumeMixer as mm
import ColetorUSB as cusb
import time


# Informacoes do modulo visto pela interface grafica
class Module:
    def __init__(self, appName="", fisicalIndex=-1):
        self.AppName = appName
        self.FisicalIndex = fisicalIndex

    def getAppName(self):
        return self.AppName

    def getFisicalIndex(self):
        return self.FisicalIndex

    def setAppName(self, name):
        self.appName = name

    def setFisicalIndex(self, index):
        self.FisicalIndex = index

# Gerenciamento do grupo de modulos
class ModulesCollection:
    def __init__(self):
        self.Modules = []

    def AddModulo(self, appName, fisicalIndex):
        self.Modules.append(Module(appName, fisicalIndex))

    def CreateCollection(self, DicValues):
        self.Modules = []
        for elem, index in zip(DicValues, range(len(DicValues))):
            self.AddModulo(DicValues[elem], index)

    def GetCollection(self):
        return self.Modules

    def GetNomeFonte(self, moduleIndex):
        for module in self.Modules:
            if moduleIndex == module.getFisicalIndex():
                return module.getAppName()
        return []


class ModMixerGUI:
    def __init__(self):
        self.janelaAberta = False
        self.usbColetor = cusb.ColetorUSB()
        self.mixer = mm.Mixer("User")
        self.modules = ModulesCollection()
        self.numerModulos = -1
        self.refreshTimeoutTime = 5
        self.NumeroMaximoModulos = 3
        self.Layouts = {"Iniciando": self.CreateLayoutMixerIniciando(),
                        "Ativado": self.CreateLayoutMixerAtivado(),
                        "Desativado": self.CreateLayoutMixerDesativado()}

        self.dicEstadosJanela = { "None": 0,"Iniciando":1, "Ativado":2, "Desativado":3}
        self.estadoJanela = self.dicEstadosJanela["None"]
        
    def setEstadoLayout(self, estado):
        self.estadoJanela = estado

    def IdentificaEstadoJanela(self):
        if(self.numerModulos < 0):
            return(self.dicEstadosJanela["Iniciando"])
        elif(self.numerModulos == 0):
            return(self.dicEstadosJanela["Desativado"])
        else:
            return(self.dicEstadosJanela["Ativado"])

    def AtualizaNumeroModulos(self, nModules):
        print("Numero de modulos:",nModules)
        self.numerModulos = nModules

    def getNumeroModulos(self):
        return self.numerModulos

    def getApplicationsName(self):
        nomes = self.mixer.GetNomeFontes()
        return nomes

    def AtualizaEscolhasIndex(self, DicValues):
        self.modules.CreateCollection(DicValues)

    def setVisibles(self):
        for index in range(self.NumeroMaximoModulos):
            if index < self.getNumeroModulos():
                isVisible = True
            else:
                isVisible = False

            self.win["volumeBar" + str(index)].Update(visible=isVisible)
            self.win["apps_List" + str(index)].Update(visible=isVisible)
            self.win["mixer_line" + str(index)].Update(visible=isVisible)

    def CreateLayoutMixerAtivado(self):
        nomes_app = self.getApplicationsName()
        nomes_app.append("none")

        layout = []
        title_line = psg.Text(
            "Select applications", font="Arial 15", justification="center"
        )
        layout.append([title_line])

        # Gera menu para cada possivel mixer
        for index in range(self.NumeroMaximoModulos):
            mixer_line = psg.Text(
                "mixer [" + str(index) + "]",
                key="mixer_line" + str(index),
                font="Arial 15",
                justification="left",
                visible=False,
            )

            layout.append(
                [
                    psg.Combo(nomes_app, key="apps_List" + str(index), visible=False),
                    mixer_line,
                ]
            )

            layout.append(
                [
                    psg.ProgressBar(
                        max_value=1.2,
                        orientation="h",
                        bar_color=("green", "grey"),
                        style="vista",
                        size=(22, 5),
                        key="volumeBar" + str(index),
                        visible=False,
                    )
                ]
            )
        layout.append([psg.Button("Refresh APP's list"), psg.Button("Apply changes")])

        return layout

    def CreateLayoutMixerDesativado(self):
        layout = []
        mixer_line = psg.Text(
            "Please, connect the ModMixers modules",
            font="Arial 15",
            justification="center",
        )
        layout.append([mixer_line])
        return layout

    def CreateLayoutMixerIniciando(self):
        layout = []
        mixer_line = psg.Text(
            "Connecting...",
            font="Arial 45",
            justification="center",
        )
        layout.append([mixer_line])
        return layout

    def getLayout(self, estadoJanela):
        layout =[]
        if(estadoJanela == self.dicEstadosJanela["Iniciando"]):
            layout = self.Layouts["Iniciando"]
        elif(estadoJanela == self.dicEstadosJanela["Ativado"]):
            layout = self.Layouts["Ativado"]
        else:
            layout = self.Layouts["Desativado"]
        return layout

    def CriaJanela(self, novoEstadoJanela):
        # Se o layout deve ser mudado
        if(novoEstadoJanela != self.estadoJanela):
            if(self.janelaAberta):
                self.FechaJanela()

            self.janelaAberta = True
            self.setEstadoLayout(novoEstadoJanela)
            layout = self.getLayout(novoEstadoJanela)
            self.win = psg.Window("ModMixer", layout, finalize=True)

    def EhFechamento(self, event):
        if event == psg.WIN_CLOSED or event == "None":
            return True
        else:
            return False

    def AtualizaBarrasTela(self):
        # Para cada fonte selecianada no menu:
        for module in self.modules.GetCollection():
            # Coleta o volume dessa fonte
            volFonte = self.mixer.GetVolume(module.getAppName())
            # Atualiza a barra com esse valor de volume
            progress_bar = self.win["volumeBar" + str(module.getFisicalIndex())]
            progress_bar.UpdateBar(volFonte)

    def AtualizaListaApps(self):
        nomes_app = self.getApplicationsName()
        for index in range(self.NumeroMaximoModulos):
            # Atualiza nomes dos aplicativos: (atenção no 'apenas' mudar a ordem e ja alterar tudo)
            self.win["apps_List" + str(index)].update(value="", values=nomes_app)

    def FechaJanela(self):
        self.janelaAberta = False
        self.win.close()

    def LeituraDeJanela(self, timoutOn=False):
        if timoutOn:
            event, values = self.win.read(timeout=self.refreshTimeoutTime)
        else:
            event, values = self.win.read()
        return [event, values]

    def InterpretaSinal_ModuleIndex(self, moduleIndex_signal):
        try:
            moduleIndex = int(moduleIndex_signal)
        except:
            moduleIndex = -1

        # Traduz o index do mixer fisico para um nome de fonte
        nomeFonte = self.modules.GetNomeFonte(moduleIndex)
        print("NOME FONTE:", nomeFonte, ", MIXER INDEX: ", moduleIndex)
        
        # Mixer responde quais fontes pertencem este nome
        fontes = self.mixer.GetFontePorNome(nomeFonte)

        return fontes

    def InterpretaSinal_Percentual(self, percentual_signal):
        try:
            percentual = float(percentual_signal)
        except:
            raise Exception(
                "Erro de comunicacao <Sinal desconhecido>: percentual = "
                + percentual_signal
            )
        return percentual

    def InterpretaSinal_Cabecalho(self, cabecalho_signal):
        if cabecalho_signal == "F":
            cabecalho = self.mixer.Cabecalhos["Fonte"]
        elif cabecalho_signal == "G":
            cabecalho = self.mixer.Cabecalhos["Geral"]
        else:
            cabecalho = self.mixer.Cabecalhos["Iddle"]
        return cabecalho

    def InterpretaSinais(self, Sinais):

        SinaisInterpretados = []
        for [cabecalho_signal, moduleIndex_signal, percentual_signal] in Sinais:

            comando = self.InterpretaSinal_Cabecalho(cabecalho_signal)
            percentual = self.InterpretaSinal_Percentual(percentual_signal)
            fontes = self.InterpretaSinal_ModuleIndex(moduleIndex_signal)

            SinaisInterpretados.append([comando, fontes, percentual])

        return SinaisInterpretados

    def OperaEntradasJanela(self, event, values):
        print("evento::", event)
        if self.EhFechamento(event):
            self.win.close()
            quit()
        elif event == "Apply changes":
            print("Apply changes")
            self.AtualizaEscolhasIndex(values)
        elif event == "Refresh APP's list":
            print("Refresh APP's list")
            self.AtualizaListaApps()

    def OperaGUI(self, event, values):
        self.OperaEntradasJanela(event, values)
        self.AtualizaBarrasTela()
        self.setVisibles()    
    
    def OperaAplicacoes(self, SinaisInterpretados):
        # Realiza as operacoes indicadas pelos comandos traduzidos
        self.mixer.OperaComandos(SinaisInterpretados)

    def AtualizaJanela(self):
        estadoJanela = self.IdentificaEstadoJanela()
        self.CriaJanela(estadoJanela)
        return(estadoJanela)



    def RecebeSinaisModulos(self):
        # Escuta por mixers fisicos para criar layout
        Sinais, nModules = self.usbColetor.CapturaComando()
        # Traduz sinais de index para comandos conhecidos pela GUI
        comandos = self.InterpretaSinais(Sinais)
        # Atualiza conhecimento de numero de modulos conectados
        self.AtualizaNumeroModulos(nModules)

        return(comandos)


    def loop(self):
        
        Sinais = []
        while(True):
            print()
            estadoJanela = self.AtualizaJanela()
            
            if(estadoJanela == self.dicEstadosJanela["Iniciando"]):
                print("Janela inicial")
                time.sleep(0.5) 
            
            elif(estadoJanela == self.dicEstadosJanela["Ativado"]):
                print("Janela de menus")
                [event, values] = self.LeituraDeJanela(timoutOn=True)
                self.OperaGUI(event, values)
                self.OperaAplicacoes(Sinais)

            else:
                print("Janela de aguardo por modulos")
                time.sleep(0.2)
                
            Sinais = self.RecebeSinaisModulos()






# DESEJADO:

# ELE PRECISA ATUALIZAR A ESCOLHA DE INDEX SOMENTE APOS O CLIQUE
# AS OPCOES DE APP ATUALIZAM COM REFRESH OU A CADA 100ms
# AS BARRA DE VOLUME ATUALIZAM COM ALTA FREQUENCIA
# OS MIXERS APARECEM CONFORME "SOLITICADOS" PELO VOLUMEMIXER (nao pelo numero de abas)


# Melhorar organizacao das abstracoes
# Erro ao sair
# So permitir ele selecionar o app uma vez no menu
# Melhorias no design da interface
# Usar Pyinstaller para gerar instalador de dependencias
# Fazer icon da aplicação
# Comunicar com usb