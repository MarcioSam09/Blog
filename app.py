from flask import Flask, flash, render_template, request, redirect, url_for, session, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object('config')

DATABASE = 'blog.db'

# Funções auxiliares
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Rotas de Autenticação
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        senha = generate_password_hash(request.form['senha'])
        
        # Verificar se o usuário já existe
        db = get_db()
        usuario_existente = db.execute('SELECT * FROM usuarios WHERE nome_usuario = ?', (nome_usuario,)).fetchone()

        if usuario_existente:
            # Se o usuário já existir, exibe uma mensagem de erro
            flash('Atenção, usuário já existente.', 'error')
            return render_template('cadastro.html')
        
        # Caso o usuário não exista, faz o cadastro
        db.execute('INSERT INTO usuarios (nome_usuario, senha, eh_administrador) VALUES (?, ?, ?)', (nome_usuario, senha, 0))
        db.commit()
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        senha = request.form['senha']
        db = get_db()  # Função para obter a conexão com o banco de dados
        user = db.execute('SELECT * FROM usuarios WHERE nome_usuario = ?', (nome_usuario,)).fetchone()
                
        if user is None:
            # Usuário não encontrado
            return render_template('login.html', erro='Usuário não encontrado')
        
        if not check_password_hash(user['senha'], senha):
            # Senha incorreta
            return render_template('login.html', erro='Senha incorreta')
        
        # Login bem-sucedido
        session['usuario_id'] = user['id']
        session['nome_usuario'] = user['nome_usuario']
        session['eh_administrador'] = user['eh_administrador']
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Rotas do Blog
@app.route('/')
def index():
    db = get_db()
    postagens = db.execute('SELECT * FROM postagens').fetchall()
    return render_template('index.html', postagens=postagens)

@app.route('/criar_postagem', methods=['GET', 'POST'])
def criar_postagem():
    if request.method == 'POST':
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        usuario_id = session.get('usuario_id')
        db = get_db()
        db.execute('INSERT INTO postagens (titulo, conteudo, usuario_id) VALUES (?, ?, ?)', (titulo, conteudo, usuario_id))
        db.commit()
        return redirect(url_for('index'))
    return render_template('criar_postagem.html')

@app.route('/postagem/<int:postagem_id>', methods=['GET', 'POST'])
def detalhe_postagem(postagem_id):
    db = get_db()
    postagem = db.execute('SELECT * FROM postagens WHERE id = ?', (postagem_id,)).fetchone()
    comentarios = db.execute('SELECT * FROM comentarios WHERE postagem_id = ?', (postagem_id,)).fetchall()
    if request.method == 'POST':
        conteudo = request.form['conteudo']
        usuario_id = session.get('usuario_id')
        db.execute('INSERT INTO comentarios (conteudo, postagem_id, usuario_id) VALUES (?, ?, ?)', (conteudo, postagem_id, usuario_id))
        db.commit()
        return redirect(url_for('detalhe_postagem', postagem_id=postagem_id))
    return render_template('detalhe_postagem.html', postagem=postagem, comentarios=comentarios)

@app.route('/excluir_postagem/<int:postagem_id>')
def excluir_postagem(postagem_id):
    usuario_id = session.get('usuario_id')
    db = get_db()
    postagem = db.execute('SELECT * FROM postagens WHERE id = ?', (postagem_id,)).fetchone()
    if postagem['usuario_id'] == usuario_id or session.get('eh_administrador'):
        db.execute('DELETE FROM postagens WHERE id = ?', (postagem_id,))
        db.commit()
    return redirect(url_for('index'))

@app.route('/excluir_comentario/<int:comentario_id>')
def excluir_comentario(comentario_id):
    usuario_id = session.get('usuario_id')
    db = get_db()
    comment = db.execute('SELECT * FROM comentarios WHERE id = ?', (comentario_id,)).fetchone()
    if comment['usuario_id'] == usuario_id or session.get('eh_administrador'):
        db.execute('DELETE FROM comentarios WHERE id = ?', (comentario_id,))
        db.commit()
    return redirect(url_for('detalhe_postagem', postagem_id=comment['postagem_id']))

if __name__ == '__main__':
    init_db()  # Apenas para inicializar o banco de dados
    app.run(debug=True)
