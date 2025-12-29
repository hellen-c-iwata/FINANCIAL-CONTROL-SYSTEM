# Documentação Técnica do Sistema de Controle Financeiro (SCF) - Financial-control-system (FCS)

## 1. Visão Geral do Sistema

O **Sistema de Controle Financeiro (SCF)** é uma aplicação de três camadas (*Mobile*, *Backend*, *Dados*) focada na automação do agendamento, soma e notificação de despesas e receitas recorrentes.

|Camada | Tecnologia (Open Source) | Função |
|-------- | ----- | ----------- |
|Backend/API | Python (FastAPI) | Lógica de negócio, validação e comunicação com DB |
|Mobile (Frontend)|Flutter/React Native |Interface do Usuário e recebimento de notificações|
|Banco de dados | Postgres |Armazenamento persistente de transações |
|Scheduler|Celery+Redis|Automação da geração de recorrências e disparo de notificação|


## 2. Modelo de dados (Schema)

### 👤 Table: `users`
| Field | Type | Description | Validation Rules |
|--------|------|-------------|------------------|
| id | UUID | Primary key. | Auto-generated. |
| full_name | VARCHAR(150) | User’s full name. | Required. |
| username | VARCHAR(100) | Login name (e.g., john.doe). | Required, unique. |
| password_hash | VARCHAR(255) | Encrypted user password. | Required. |
| role | ENUM('ADMIN', 'USER') | User role in the system. | Required. |
| status | ENUM('ACTIVE', 'INACTIVE', 'BLOCKED') | Account status. | Default: ACTIVE. |
| created_at | TIMESTAMP | Record creation timestamp. | Default: CURRENT_TIMESTAMP. |
| updated_at | TIMESTAMP | Last update timestamp. | Auto-updated. |

---

### 💸 Table: `expense_templates`
| Field | Type | Description | Validation Rules |
|--------|------|-------------|------------------|
| id | UUID | Primary key. | Auto-generated. |
| user_id | UUID (FK → users.id) | Owner of this expense rule. | Required. |
| category_id | UUID (FK → category_templates.id) | Related category. | Required. |
| description | VARCHAR(200) | Expense name (e.g., Rent, Netflix). | Required. |
| recurrence_type | ENUM('MONTHLY', 'BIWEEKLY', 'INSTALLMENT', 'ONE_TIME') | Type of recurrence. | Required. |
| amount | DECIMAL(10,2) | Expense amount per cycle or installment. | Required (> 0). |
| reference_date | DATE | Initial date for recurrence generation. | Required. |
| due_day | INT | Fixed due day (1–31). | Required for MONTHLY and INSTALLMENT. |
| total_installments | INT | Number of installments if applicable. | Required if INSTALLMENT (>1). |
| generated_installments | INT | Counter for generated instances. | Default 0. |
| is_active | BOOLEAN | Whether to continue generating new instances. | Default TRUE. |
| created_at | TIMESTAMP | Record creation timestamp. | Default: CURRENT_TIMESTAMP. |

---

### 💰 Table: `income_templates`
| Field | Type | Description | Validation Rules |
|--------|------|-------------|------------------|
| id | UUID | Primary key. | Auto-generated. |
| user_id | UUID (FK → users.id) | Owner of this income rule. | Required. |
| category_id | UUID (FK → category_templates.id) | Related category. | Required. |
| description | VARCHAR(200) | Income name (e.g., Salary, Bonus). | Required. |
| amount | DECIMAL(10,2) | Income amount per cycle. | Required (> 0). |
| reference_date | DATE | Start date for recurrence. | Required. |
| recurrence_type | ENUM('MONTHLY', 'ONE_TIME') | Type of income recurrence. | Required. |
| is_active | BOOLEAN | Whether new instances should be generated. | Default TRUE. |
| created_at | TIMESTAMP | Record creation timestamp. | Default: CURRENT_TIMESTAMP. |

---

### 🏷️ Table: `category_templates`
| Field | Type | Description | Validation Rules |
|--------|------|-------------|------------------|
| id | UUID | Primary key. | Auto-generated. |
| name | VARCHAR(100) | Category name (e.g., Food, Transport). | Required, unique. |
| description | VARCHAR(255) | Category details. | Optional. |
| type | ENUM('EXPENSE', 'INCOME') | Category type. | Required. |
| created_at | TIMESTAMP | Record creation timestamp. | Default: CURRENT_TIMESTAMP. |

---

### 💼 Table: `expense_instances`
| Field | Type | Description | Validation Rules |
|--------|------|-------------|------------------|
| id | UUID | Primary key. | Auto-generated. |
| template_id | UUID (FK → expense_templates.id) | Related expense template. | Required. |
| due_date | DATE | Exact payment due date. | Required. |
| amount | DECIMAL(10,2) | Final payable amount. | Required. |
| status | ENUM('PAID', 'UNPAID', 'OVERDUE') | Payment status. | Default: UNPAID. |
| installment_number | INT | Installment number (if applicable). | Required if INSTALLMENT. |
| paid_at | DATE | Date when payment was completed. | Optional. |
| created_at | TIMESTAMP | Record creation timestamp. | Default: CURRENT_TIMESTAMP. |

---

### 💵 Table: `income_instances`
| Field | Type | Description | Validation Rules |
|--------|------|-------------|------------------|
| id | UUID | Primary key. | Auto-generated. |
| template_id | UUID (FK → income_templates.id) | Related income template. | Required. |
| receive_date | DATE | Expected or actual receive date. | Required. |
| amount | DECIMAL(10,2) | Received amount. | Required. |
| status | ENUM('RECEIVED', 'PENDING') | Income status. | Default: PENDING. |
| received_at | DATE | Actual date received (if applicable). | Optional. |
| created_at | TIMESTAMP | Record creation timestamp. | Default: CURRENT_TIMESTAMP. |

---

### 🏷️ Table: `category_instances`
| Field | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key. |
| category_id | UUID (FK → category_templates.id) | Source category. |
| type | ENUM('EXPENSE', 'INCOME') | Category type inherited from template. |
| created_at | TIMESTAMP | Creation timestamp. |

---

### 👥 Table: `user_sessions`
| Field | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key. |
| user_id | UUID (FK → users.id) | Related user. |
| last_login | TIMESTAMP | Last successful login. |
| failed_attempts | INT | Failed login attempts. |
| blocked_at | TIMESTAMP | Block timestamp if account locked. |

---

### 🔗 Relationships Summary

| Relationship | Type |
|---------------|------|
| 1 User → N Expense Templates | One-to-Many |
| 1 User → N Income Templates | One-to-Many |
| 1 Category Template → N Expense Templates | One-to-Many |
| 1 Category Template → N Income Templates | One-to-Many |
| 1 Expense Template → N Expense Instances | One-to-Many |
| 1 Income Template → N Income Instances | One-to-Many |





## 3. Contratos da API (Endpoints Principais)
|     Funcionalidade      | Método HTTP |     Endpoind URI    |      Descrição                    | Lógica de Negócio |
| ----------------------- | ----------- | ------------------- | --------------------------------- | -----------       |
| Criar usuário           | POST        | /v1/users           | Cria um novo usuário              | Valida os campos obrigatórios
| Criar categoria         | POST        | /v1/categories      | Cria uma nova categoria           | Valida o nome da categoria; verifica se ja existe uma categoria com o mesmo nome; se não existir, insere no banco e retorna os dados criados.
| Criar Receita           | POST        | /v1/income          | Cria uma nova receita             | Valida os campos obrigatórios (valor, descrição, data e categoria) associa ao usuario autenticado; grava no banco e retorna os dados criados.
| Criar Despesa           | POST        | /v1/expenses        | Cria uma nova despesa             | Valida os campos obrigatórios (valor, descrição, data vencimento e categoria); associa categoria e usuario; grava e retorna o registro criado.
| Listar categorias       | GET         | /v1/categories      | Lista todas as categorias         | Retorna todas as categorias cadastradas do usuario autenticado
| Listar Receitas         | GET         | /v1/income          | Lista todas as receitas           | Retorna todas as receitas cadastradas do usuario autenticado
| Listar Despesas         | GET         | /v1/expenses        | Lista todas as despesas           | Retorna todas as despesas cadastradas do usuario autenticado
| Bucar cartegoria por id | GET         | /v1/categories/{id} | Retorna uma categoria específica  | Busca a categoria pelo id; se não encontrada, retorna erro 4040; caso exista, retorna os dados da categoria
| Bucar Receita por id    | GET         | /v1/income/{id}     | Retorna uma receita específica    | Busca a receita pelo id; se não encontrada, retorna erro 404; caso exista, retorna os dados da receita
| Bucar Despesa por id    | GET         | /v1/expenses/{id}   | Retorna uma despesa específica    | Busca despesas pelo id; se não encontrada, retorna erro 404; caso exista, retorna os dados da despesa (incluindo status de pagamento)
| Atualizar categoria     | PATCH       | /v1/categories/{id} | Atualiza uma categoria específica | Verifica se a categoria existe, aplica apenas os campos enviados na requisição; salva alteração e retorna os dados atualizados.
| Atualizar Receita       | PATCH       | /v1/income/{id}     | Atualiza uma receita específica   | Valida campos modificados; atualiza valores, categoria ou data; registra a data de atualização e retorna os dados atualizados.
| Atualizar Despesa       | PATCH       | /v1/expenses/{id}   | Atualiza uma despesa específica   | Permite alterar valor, categoria, data, status ou condição, valida se a despesa existe e salva as alterações.
| Deletar categoria       | DELETE      | /v1/categories/{id} | Exclui uma categoria específica   | Verifica se há receita/despesas vinculadas; se não houver, remove; caso contrário, retorna erro de vinculo com os dados.
| Deletar Receita         | DELETE      | /v1/income/{id}     | Exclui uma receita específica     | Verifica se a receita existe; remove do banco e retorna confirmação.
| Deletar Despesa         | DELETE      | /v1/expenses/{id}   | Exclui uma despesa específica     | Verifica se a despesa existe; remove do banco e retorna confirmação.
| Deletar usuário         | DELETE      | /v1/users/{id}      | Exclui um usuário                 | Verifica se o usuario existe; remove do banco e retorna confirmação.


## 4. Lógica do Módulo de Agendamento (Scheduler)
O Job roda **diariamente** e gera as `expense_instances` com antecendência de 45 dias;
| CONDIÇÂO | LÓGICA DE VENCIMENTO | FINALIZAÇÃO |
|----------|----------------------|-------------|
|Mensal    | Vence no `dia_vencimento` fixo do mês subsequente. | Geração contínua (infinito) |
|Parcelado | Vence no `dia_vencimento` fixo do mês subsquente, até `total_parcelas` | `ativo` = FALSE ao atingir total_parcelas.|
|Quinzenal | Vence no `ultima_data_vencimento + 15 dias`. | Gereção contínua (infinito) |
|Unica     | Vence na `data_referencia` | `ativo` = FALSE e `parcelas_geradas` = 1 após a primeira geração |

## 5. Módulo de Notificação 
| GATILHO | DATA-ALVO | CONTEÚDO (PAYLOAD) |
|---------|-----------| ------------------ |
| Aviso prévio | Vencimento em **Hoje+3 dias** | Soma total + relatório simples de itens (Descrição, valor, Condição, Parcela).|
| Vencimento Hoje | Vencimento em **HOJE** | Soma toal + relatório simples de itens |
| Filtro | Apenas despesas com `status` = '**Não Pago**' | |
