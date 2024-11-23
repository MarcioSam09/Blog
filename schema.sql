CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_usuario TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    eh_administrador BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS postagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conteudo TEXT NOT NULL,
    postagem_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (postagem_id) REFERENCES postagens(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
