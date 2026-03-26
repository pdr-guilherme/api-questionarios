# Requisitos do sistema de questionários

## Objetivo

Desenvolver um sistema de questionários em Django / DRF onde:

- o administrador cria e gerencia questionários;
- cada questionário possui perguntas com alternativas;
- as perguntas podem possuir imagens associadas;
- o administrador também cria os usuários que irão responder;
- o usuário comum acessa os questionários disponíveis e envia suas respostas;
- o administrador acompanha o progresso e os resultados.

---

## Perfis do sistema

### Administrador

Deve conseguir:

- criar usuários que participarão dos questionários;
- criar, editar, publicar e encerrar questionários;
- montar perguntas e alternativas;
- associar imagens às perguntas;
- acompanhar andamento das respostas;
- visualizar respostas enviadas pelos usuários;
- consultar quais usuários ainda não responderam, quais estão em andamento e quais concluíram.

### Usuário comum

Deve conseguir:

- acessar os questionários disponíveis para ele;
- visualizar as perguntas e respectivas imagens;
- selecionar respostas;
- salvar o progresso;
- continuar depois de onde parou;
- finalizar o questionário quando concluir.

---

## Funcionalidades principais

## 1. Gestão de usuários pelo administrador

O sistema deve permitir que o administrador:

- cadastre usuários que irão responder os questionários;
- edite dados desses usuários;
- ative ou desative acesso quando necessário;
- visualize a lista de usuários cadastrados;
- relacione os usuários ao contexto de resposta dos questionários.

### Regras

- somente administrador pode criar usuários respondentes;
- o usuário comum não pode criar conta por conta própria, salvo se isso for definido no futuro;
- usuários inativos não devem conseguir responder questionários.

---

## 2. Gestão de questionários

O sistema deve permitir que o administrador:

- crie um novo questionário;
- edite questionários ainda não encerrados;
- salve questionário como rascunho;
- publique questionário para resposta;
- encerre um questionário;
- organize a ordem das perguntas.

### Regras

- questionários em rascunho não podem ser respondidos;
- questionários publicados podem ser respondidos;
- questionários encerrados não aceitam novas respostas;
- alterações estruturais em questionários já respondidos devem ser tratadas com cuidado para evitar inconsistência.

---

## 3. Gestão das perguntas

O sistema deve permitir que o administrador:

- adicione perguntas ao questionário;
- defina a ordem de exibição;
- marque perguntas como obrigatórias ou não;
- configure as alternativas de resposta;
- associe uma ou mais imagens à pergunta.

### Regras

- cada pergunta deve pertencer a um questionário;
- cada pergunta deve possuir alternativas válidas para resposta;
- perguntas obrigatórias precisam ser respondidas para conclusão do questionário;
- a ordenação deve ser respeitada na exibição.

---

## 4. Resposta do questionário pelo usuário

O sistema deve permitir que o usuário comum:

- visualize apenas os questionários disponíveis para ele;
- abra um questionário;
- navegue pelas perguntas em ordem;
- visualize imagens relacionadas à pergunta;
- selecione uma resposta para cada pergunta;
- salve o progresso parcial;
- retorne posteriormente para continuar;
- finalize o envio.

### Regras

- o usuário não pode responder questionários não publicados;
- o sistema deve impedir conclusão com perguntas obrigatórias sem resposta;
- após finalização, o comportamento deve seguir a regra definida pelo projeto, preferencialmente sem permitir edição;
- o sistema deve manter o histórico do progresso do usuário.

---

## 5. Acompanhamento de progresso

O sistema deve permitir que o administrador acompanhe:

- total de usuários vinculados ao processo de resposta;
- quantos ainda não iniciaram;
- quantos estão com resposta em andamento;
- quantos concluíram;
- percentual de progresso por usuário;
- data de início e conclusão de cada resposta;
- detalhamento do que foi respondido.

### Regras

- o administrador deve ter visão consolidada por questionário;
- o administrador deve conseguir filtrar por status de resposta;
- o usuário comum só pode visualizar as próprias respostas, nunca as de outros usuários.

---

## 6. Requisitos funcionais

### RF01
O sistema deve permitir ao administrador criar usuários respondentes.

### RF02
O sistema deve permitir ao administrador editar e gerenciar usuários respondentes.

### RF03
O sistema deve permitir ao administrador criar questionários.

### RF04
O sistema deve permitir ao administrador montar perguntas e alternativas dentro do questionário.

### RF05
O sistema deve permitir ao administrador associar imagens às perguntas.

### RF06
O sistema deve permitir ao administrador publicar e encerrar questionários.

### RF07
O sistema deve permitir ao usuário visualizar os questionários disponíveis.

### RF08
O sistema deve permitir ao usuário responder às perguntas.

### RF09
O sistema deve permitir salvar progresso parcial.

### RF10
O sistema deve permitir retomada posterior do questionário em andamento.

### RF11
O sistema deve validar o preenchimento obrigatório antes da finalização.

### RF12
O sistema deve permitir ao administrador visualizar o progresso individual e geral das respostas.

### RF13
O sistema deve permitir ao administrador visualizar o conteúdo das respostas enviadas.

---

## Requisitos não funcionais

### RNF01 Segurança

- autenticação obrigatória;
- separação clara entre permissões de administrador e usuário comum;
- usuário comum acessa apenas seus próprios dados.

### RNF02 Integridade

- respostas precisam ser consistentes com as alternativas disponíveis;
- o sistema não deve permitir respostas inválidas ou fora do contexto da pergunta;
- deve haver controle para evitar duplicidade indevida de resposta.

### RNF03 Performance

- listagens administrativas devem ser paginadas;
- a exibição de questionários com perguntas, imagens e alternativas deve ser otimizada.

### RNF04 Auditoria

- registrar criação, alteração, início e conclusão;
- registrar quem criou o questionário e quem respondeu.

---

## Fluxo esperado

### Fluxo do administrador

1. Cadastra os usuários respondentes.
2. Cria o questionário.
3. Adiciona perguntas, alternativas e imagens.
4. Publica o questionário.
5. Acompanha quem iniciou, quem concluiu e as respostas enviadas.
6. Encerra o questionário quando necessário.

### Fluxo do usuário

1. Acessa o sistema.
2. Visualiza os questionários disponíveis.
3. Inicia um questionário.
4. Responde parcialmente ou totalmente.
5. Salva o andamento.
6. Finaliza quando concluir.

---

## Critérios de aceite

O sistema será considerado aceito quando:

- o administrador conseguir criar usuários respondentes;
- o administrador conseguir criar e publicar questionários;
- o administrador conseguir adicionar perguntas, alternativas e imagens;
- o usuário conseguir responder o questionário normalmente;
- o sistema salvar progresso parcial corretamente;
- o usuário conseguir continuar de onde parou;
- o administrador conseguir acompanhar o status das respostas;
- o administrador conseguir visualizar as respostas enviadas;
- as regras de permissão estiverem funcionando corretamente.

---

## O que deve ficar em aberto para você definir

Como parte da implementação, quero que você proponha e defina:

- a modelagem das entidades;
- os relacionamentos entre elas;
- os campos necessários;
- a estratégia de serialização;
- a organização das views/endpoints;
- as validações de domínio;
- as permissões e separação entre área administrativa e área do usuário.

A ideia aqui é avaliar sua capacidade de modelagem, organização e tomada de decisão técnica dentro do contexto de um projeto em Django / DRF.