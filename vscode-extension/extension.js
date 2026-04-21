// extension.js — Neglish VS Code Extension
// Minimal activation — all features are grammar/snippet based

const vscode = require('vscode');

function activate(context) {
    console.log('Neglish Language Support activated!');

    // Register a "Run Neglish File" command
    const runCmd = vscode.commands.registerCommand('neglish.runFile', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active file!');
            return;
        }

        const filePath = editor.document.fileName;
        if (!filePath.endsWith('.neg')) {
            vscode.window.showErrorMessage('Not a .neg file!');
            return;
        }

        // Save first
        editor.document.save().then(() => {
            const terminal = vscode.window.createTerminal('Neglish');
            terminal.show();
            terminal.sendText(`python main.py "${filePath}" --nogui`);
        });
    });

    // Register "Run with GUI" command
    const runGuiCmd = vscode.commands.registerCommand('neglish.runFileGui', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;
        const filePath = editor.document.fileName;
        editor.document.save().then(() => {
            const terminal = vscode.window.createTerminal('Neglish GUI');
            terminal.show();
            terminal.sendText(`python main.py "${filePath}"`);
        });
    });

    context.subscriptions.push(runCmd, runGuiCmd);

    // Status bar item
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBar.text = '$(play) Run Neglish';
    statusBar.command = 'neglish.runFile';
    statusBar.tooltip = 'Run the current .neg file';
    context.subscriptions.push(statusBar);

    // Show status bar only for .neg files
    const updateStatusBar = () => {
        const editor = vscode.window.activeTextEditor;
        if (editor && editor.document.fileName.endsWith('.neg')) {
            statusBar.show();
        } else {
            statusBar.hide();
        }
    };

    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(updateStatusBar)
    );
    updateStatusBar();
}

function deactivate() {}

module.exports = { activate, deactivate };
