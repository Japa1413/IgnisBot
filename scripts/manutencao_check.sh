#!/bin/bash
# Script de Verificação de Manutenção - IgnisBot
# Executa verificações de saúde e manutenção

set -e

echo "============================================================"
echo "VERIFICAÇÃO DE MANUTENÇÃO - IGNISBOT"
echo "============================================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
PASSED=0
FAILED=0
WARNINGS=0

# Função para verificar comando
check_cmd() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅${NC} $1 encontrado"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌${NC} $1 não encontrado"
        ((FAILED++))
        return 1
    fi
}

# Função para verificar vulnerabilidades
check_safety() {
    echo ""
    echo "--- Verificando Vulnerabilidades (Safety) ---"
    if command -v safety &> /dev/null; then
        if safety check --json 2>/dev/null | grep -q '"vulnerabilities":\[]'; then
            echo -e "${GREEN}✅${NC} Nenhuma vulnerabilidade encontrada"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠️${NC} Vulnerabilidades encontradas"
            safety check
            ((WARNINGS++))
        fi
    else
        echo -e "${YELLOW}⚠️${NC} Safety não instalado (pip install safety)"
        ((WARNINGS++))
    fi
}

# Função para verificar dependências desatualizadas
check_outdated() {
    echo ""
    echo "--- Verificando Dependências Desatualizadas ---"
    if pip list --outdated 2>/dev/null | grep -q .; then
        echo -e "${YELLOW}⚠️${NC} Dependências desatualizadas encontradas:"
        pip list --outdated
        ((WARNINGS++))
    else
        echo -e "${GREEN}✅${NC} Todas as dependências estão atualizadas"
        ((PASSED++))
    fi
}

# Função para verificar testes
check_tests() {
    echo ""
    echo "--- Verificando Testes ---"
    if command -v pytest &> /dev/null; then
        if pytest tests/ -v --tb=short 2>/dev/null; then
            echo -e "${GREEN}✅${NC} Todos os testes passando"
            ((PASSED++))
        else
            echo -e "${RED}❌${NC} Alguns testes falharam"
            ((FAILED++))
        fi
    else
        echo -e "${YELLOW}⚠️${NC} pytest não instalado"
        ((WARNINGS++))
    fi
}

# Main
echo "Verificando comandos necessários..."
check_cmd python
check_cmd pip
check_cmd git

check_safety
check_outdated
check_tests

# Resumo
echo ""
echo "============================================================"
echo "RESUMO"
echo "============================================================"
echo -e "${GREEN}✅ Passou:${NC} $PASSED"
echo -e "${RED}❌ Falhou:${NC} $FAILED"
echo -e "${YELLOW}⚠️ Avisos:${NC} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Sistema saudável!${NC}"
    exit 0
else
    echo -e "${RED}❌ Problemas encontrados. Verifique acima.${NC}"
    exit 1
fi

