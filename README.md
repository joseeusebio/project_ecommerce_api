# Ecommerce Api
Api Rest para gestão de produtos em um Ecommerce

## Configurando do Ambiente

Siga os passos abaixo para conseguir utilizar o sistema

### Clonar o repositório
1. git clone [https://github.com/joseeusebio/project_bringel.git](https://github.com/joseeusebio/project_ecommerce_api.git)

### Criação de um Virtual Enviroment
1. python -m venv .venv
2. Unix ou MacOs - source .venv/Scripts/Activate
3. Windows - venv\Scripts\activate

### Criação de um arquivo .env para incluir as variáveis de ambiente.
1. Dentro da pasta dotenv_files crie um novo arquivo (mkdir .env) e utilize o modelo de exemplo .env-example para preencher as variáveis de ambiente necessárias.

### Iniciando o build do container docker
 1. Após a criação do arquivo .env execute o comando docker-compose up --build no console na raiz do projeto e aguarde a criação dos containners.

### Criação do superuser para utilizar os endpoints da API
1. Após a criação dos containners execute o seguinte comando no shell do docker djangoapi (python manage.py createsuperuser) esse usuário será importante para acessar a página de administração do django para criar novos usuários ou então utiliza-lo para acessar os endpoints.

### Acessar a documentação da API

1. Para acessar a documentação da API basta acessar os links  http://localhost:8000/swagger/ ou http://localhost:8000/redoc/ após subir aplicação.
2. Para conseguir utilizar os endpoins é necessário a geração de um token JWT através do enpoint http://localhost:8000/api/token/ utilizando o usuário que foi criado anteriormente. Para mais detalhes do verifique a documentação.


