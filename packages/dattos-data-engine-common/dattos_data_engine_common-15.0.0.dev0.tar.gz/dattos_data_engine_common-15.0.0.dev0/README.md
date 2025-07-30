# dattos-data-engine-common

Este repositório contém classes e métodos para abstração de estratégias de armazenamento de dados.

## Estrutura do Projeto

- `aws_strategy.py`: classe que implementa a estratégia de armazenamento para AWS.
- `azure_strategy.py`: classe que implementa a estratégia de armazenamento para Azure.
- `base.py`: classe base que define a interface para as estratégias de armazenamento.
- `__init__.py`: módulo que define a fábrica de instâncias para as estratégias de armazenamento.
- `requirements.txt`: lista de dependências necessárias para o projeto.

## Como Usar

Para usar as estratégias de armazenamento, é necessário instanciar a classe `StorageStrategy` com a string de conexão para o provedor de armazenamento desejado.

Exemplo:

```python
from dattos_data_engine_common import StorageStrategy

# Exemplo para AWS
aws_connection_string = "aws://access_key:secret_key@bucket"
aws_storage = StorageStrategy(aws_connection_string)
aws_storage.save("arquivo.txt", b"conteúdo do arquivo")

# Exemplo para Azure
azure_connection_string = "azure://account_name:account_key@container"
azure_storage = StorageStrategy(azure_connection_string)
azure_storage.save("arquivo.txt", b"conteúdo do arquivo")
```
