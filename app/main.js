const { app, BrowserWindow, globalShortcut, Tray, Menu, ipcMain} = require('electron');
const path = require('path');
const { spawn } = require('child_process');
let mainWindow;
let tray = null;
let pythonProcess = null;
let isQuitting = false; 


//function pour lancé le backend python
function startPythonBackend() {
  let backendPath;
  if (app.isPackaged) {
    backendPath = path.join(process.resourcesPath, 'backend', 'main.exe');
  } else {
    backendPath = path.join(__dirname, 'resources', 'backend', 'main.exe');
  }
  if (!pythonProcess) {
    pythonProcess = spawn(backendPath);
  }
}

//function pour définir les paramètre de la fenètre
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    frame: false,         
    transparent: true,    
    resizable: false,     
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false 
    }
  });

  mainWindow.loadFile('index.html');

  //ferme pas la fenêtre mais la réduit a la place
  mainWindow.on('close', (event) => {
    if (!isQuitting) {

      event.preventDefault();

      mainWindow.hide();
    }

  });
}

//définir les paramètre du tray
function createTray() {

  const iconPath = path.join(__dirname, 'icon.png');
  tray = new Tray(iconPath);


  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Ouvrir mon app',
      click: () => {
        mainWindow.show();
      }
    },
    { type: 'separator' },
    {
      label: 'Quitter',
      click: () => {
        isQuitting = true; 
        app.quit();
      }
    }
  ]);

  tray.setToolTip('Skip Genshin');
  tray.setContextMenu(contextMenu);


  tray.on('click', () => {
    mainWindow.show();
  });
}

//définition des évènement
ipcMain.on('minimize-app', () => {
  mainWindow.minimize();
});

ipcMain.on('close-app', () => {
  mainWindow.close(); 
});

let is_app_activate = false
ipcMain.on('activate-app', () => {
  is_app_activate = true
  //envoie une requête a l'api python
  fetch("http://127.0.0.1:8000/activate", {method: "POST"} )
});

ipcMain.on('desactivate-app', () => {
  is_app_activate = false
  //envoie une requête a l'api
  fetch("http://127.0.0.1:8000/desactivate", {method: "POST"} )
});

ipcMain.on('update-shortcut', (event, newShortcut) => {
  register_keybind(newShortcut)
})



//function pour définir un nouveau racourci d'activation
let currentShortcut = 'CommandOrControl+Q'

function register_keybind(new_key) {
    globalShortcut.unregister(currentShortcut)
    globalShortcut.register(new_key, () => {
    //envoie a l'interface une requete
    mainWindow.webContents.send('changement');
    is_app_activate = !is_app_activate
    //requête a l'api python
    if (is_app_activate) {
      fetch("http://127.0.0.1:8000/activate", {method: "POST"} )
    } else {
      fetch("http://127.0.0.1:8000/desactivate", {method: "POST"} )
    }
  });
}
app.on('will-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill('SIGKILL'); 
  }
  globalShortcut.unregisterAll();
});

//script au lancement de l'application
app.whenReady().then(() => {
  createWindow();
  startPythonBackend()
  createTray();
  register_keybind("CommandOrControl+Q")
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});