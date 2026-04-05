# 🦷 Triagem Para Todos Odontológica

> Sistema web e mobile para digitalização do processo de triagem da Clínica Odontológica de Ensino (COE) da UniEVANGÉLICA.

---

## 📌 Sobre o Projeto

O **Triagem Para Todos Odontológica** é uma aplicação desenvolvida como projeto extensionista com o objetivo de **digitalizar o processo de triagem de pacientes**, tornando o atendimento mais acessível, organizado e eficiente.

Atualmente, o processo de triagem é realizado de forma presencial ou por telefone, gerando:

* sobrecarga da equipe
* aumento do tempo de espera
* dificuldade de acesso ao serviço

Este sistema propõe uma solução digital simples e acessível para resolver esses problemas.

---

## 🎯 Objetivo

Permitir que pacientes realizem sua triagem de forma online, reduzindo a necessidade de deslocamento e otimizando o fluxo de atendimento da clínica.

---

## 👥 Usuários do Sistema

* 👤 **Usuário (Paciente)**

  * Cadastro e login
  * Preenchimento da triagem
  * Visualização do agendamento

* 🏥 **Equipe Administrativa**

  * Visualização das triagens
  * Organização dos atendimentos

---

## 🚀 Funcionalidades (MVP)

* ✅ Cadastro de usuário
* ✅ Login com e-mail e senha
* ✅ Recuperação de senha
* ✅ Preenchimento de formulário de triagem
* ✅ Seleção de serviço:

  * Tratamento geral
  * Prótese
  * Pediatria
  * Emergência
* ✅ Seleção de período:

  * Matutino
  * Vespertino
  * Noturno
* ✅ Armazenamento dos dados em banco
* ✅ Exibição de confirmação (pré-agendamento)
* ✅ Visualização das triagens (equipe)

---

## 🧠 Arquitetura

O sistema segue o modelo **cliente-servidor**:

```text
Usuário (Browser)
↓
Frontend (HTML, CSS, JS)
↓
Backend (Python API)
↓
Banco de Dados (MySQL)
```

---

## 🗄️ Modelo de Dados (MER)

### Usuário

* id_usuario (PK)
* nome
* email
* senha
* telefone

### Triagem

* id_triagem (PK)
* id_usuario (FK)
* serviço
* período
* data_solicitação

---

## 🛠️ Tecnologias Utilizadas

### 🌐 Web

* HTML
* CSS
* JavaScript
* Git & GitHub

### ⚙️ Backend

* Python
* MySQL

### 📱 Mobile

* React Native (em desenvolvimento)

---

## 📁 Estrutura do Projeto

```text
triagem-para-todos-odontologica/
│
├── Mobile/
├── Web/
│   ├── assets/
│   ├── backend/
│   ├── database/
│   ├── pages/
│   └── docs/
│
└── README.md
```

---

## 📅 Planejamento (Sprints)

### 🟢 Sprint 1

* Configuração do ambiente
* Cadastro e login
* Banco de dados

### 🔵 Sprint 2

* Formulário de triagem
* Navegação entre telas

### 🟡 Sprint 3

* Persistência no banco
* Painel administrativo

### 🔴 Sprint 4

* Tela de confirmação
* Ajustes de UI/UX
* Testes finais

---

## ⚠️ Limitações do MVP

* Sem integração com sistemas existentes
* Interface simples (foco em funcionalidade)
* Sem notificações automáticas
* Sem autenticação avançada

---

## 🌍 Impacto Social

O sistema contribui para:

* ✔️ Maior acessibilidade ao atendimento odontológico
* ✔️ Redução da sobrecarga da equipe
* ✔️ Melhor organização dos dados
* ✔️ Diminuição do tempo de espera

---

## 📌 Próximos Passos

* 🔔 Notificações automáticas (WhatsApp/E-mail)
* 📊 Dashboard com métricas
* 🔐 Melhorias de segurança
* ☁️ Deploy em produção
* 🔗 Integração com sistemas da clínica

---

## 👨‍💻 Equipe

* Lucas Marques Maciel
* Tito Costa Ribeiro
* Cristiano Machado dos Santos
* Jarddel Jackson Barreto da Silva
* Maria Eduarda

---

## 🔗 Repositório

👉 https://github.com/breakbalk/triagem-para-todos-odontologica

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos.
