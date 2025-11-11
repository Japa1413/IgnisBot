# 🐛 Debug Dockerfile - ModuleNotFoundError

## 🔍 Problema

O erro `ModuleNotFoundError: No module named 'utils.config'` persiste mesmo após várias correções.

## ✅ O que foi feito

1. ✅ Adicionado `PYTHONPATH=/app` no Dockerfile
2. ✅ Criado `utils/__init__.py`
3. ✅ Simplificado `.dockerignore`
4. ✅ Usado `COPY . .` para copiar tudo
5. ✅ Adicionado verificação de arquivos no build

## 🔍 Próximo Passo: Verificar Logs do Build

Após o próximo deploy, verifique os logs do **BUILD** (não do container):

1. No Railway, vá em **Deployments**
2. Clique no deployment
3. Veja a seção **"Build Logs"** (não "Runtime Logs")
4. Procure por estas mensagens:
   - `✓ utils/config.py exists`
   - `✓ utils/__init__.py exists`
   - `✓ ignis_main.py exists`

### Se aparecer `✗ MISSING`:

Isso significa que os arquivos não estão sendo copiados. Possíveis causas:
- `.dockerignore` ainda está ignorando algo
- Build context está errado
- Arquivos não estão no repositório

### Se aparecer `✓ exists`:

Os arquivos estão sendo copiados, mas o Python não os encontra. Possíveis causas:
- `PYTHONPATH` não está sendo aplicado
- Problema com permissões
- Estrutura de diretórios incorreta

## 🛠️ Soluções Alternativas

### Solução 1: Verificar Build Context

O Railway pode estar usando um build context diferente. Verifique:
- O repositório está conectado corretamente?
- Todos os arquivos estão commitados?
- O branch correto está sendo usado?

### Solução 2: Usar Buildpack ao invés de Dockerfile

Se o problema persistir, podemos tentar usar o buildpack do Railway:

1. No Railway, vá em **Settings**
2. Vá em **"Build"**
3. Mude de "Dockerfile" para "Nixpacks" ou "Buildpack"
4. Railway detectará automaticamente Python

### Solução 3: Dockerfile Alternativo

Se necessário, podemos criar um Dockerfile mais explícito que lista cada arquivo.

## 📋 Checklist de Debug

- [ ] Verificar logs do BUILD (não runtime)
- [ ] Verificar se arquivos aparecem como `✓ exists`
- [ ] Verificar se `.dockerignore` não está muito restritivo
- [ ] Verificar se todos os arquivos estão no Git
- [ ] Verificar se o branch correto está sendo usado
- [ ] Testar build localmente: `docker build -t ignisbot .`

## 🧪 Testar Localmente

Para testar se o Dockerfile funciona localmente:

```bash
docker build -t ignisbot .
docker run --rm ignisbot python -c "from utils.config import TOKEN; print('OK')"
```

Se funcionar localmente mas não no Railway, o problema é com o build context do Railway.

## 📞 Próximos Passos

1. Aguarde o próximo deploy
2. Veja os logs do BUILD
3. Compartilhe as mensagens de verificação (`✓` ou `✗`)
4. Com base nisso, aplicaremos a solução correta

