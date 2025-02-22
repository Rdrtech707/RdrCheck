// backend/server.js
const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const sqlite3 = require("sqlite3").verbose();
const jwt = require("jsonwebtoken");

const app = express();
const PORT = 5000;
const SECRET_KEY = "chave_secreta_sua"; // Troque para algo seguro

app.use(cors({
  origin: "http://localhost:8501", // Streamlit rodando local
  credentials: false // não vamos usar cookies
}));
app.use(bodyParser.json());

// Conexão com banco de dados (ajuste o caminho se for diferente)
const db = new sqlite3.Database("../inspections.db", (err) => {
  if (err) {
    console.error("Erro ao conectar BD:", err);
  } else {
    console.log("BD conectado.");
  }
});

// Endpoint de login => Gera e retorna um token JWT no body
app.post("/login", (req, res) => {
  const { username, password } = req.body;
  db.get(
    "SELECT * FROM users WHERE username = ? AND password = ?",
    [username, password],
    (err, user) => {
      if (err) {
        console.error(err);
        return res.status(500).json({ error: "Erro no servidor" });
      }
      if (!user) {
        return res.status(401).json({ error: "Credenciais inválidas" });
      }
      // Gera token JWT (expira em 1 hora)
      const token = jwt.sign(
        { username: username, role: user.role },
        SECRET_KEY,
        { expiresIn: "1h" }
      );
      res.json({ token }); // retorna token no JSON
    }
  );
});

// Endpoint de validação de token => GET /session
app.get("/session", (req, res) => {
  // Espera cabeçalho Authorization: Bearer <TOKEN>
  const authHeader = req.headers["authorization"];
  if (!authHeader) {
    return res.status(401).json({ error: "Não autenticado" });
  }
  const token = authHeader.split(" ")[1];
  if (!token) {
    return res.status(401).json({ error: "Token não fornecido" });
  }
  jwt.verify(token, SECRET_KEY, (err, decoded) => {
    if (err) {
      return res.status(401).json({ error: "Token inválido ou expirado" });
    }
    // Retorna dados do usuário
    res.json({ user: decoded.username, role: decoded.role });
  });
});

app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});
