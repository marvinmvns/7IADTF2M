#!/usr/bin/env python3
"""
Script de diagnóstico: Verifica se a UI está configurada corretamente
para otimização algorítmica.
"""
import os
import sys

def check_file_content(filepath, search_strings):
    """Verifica se strings específicas estão no arquivo."""
    if not os.path.exists(filepath):
        return False, f"Arquivo não encontrado: {filepath}"

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    missing = []
    for search_str in search_strings:
        if search_str not in content:
            missing.append(search_str)

    if missing:
        return False, f"Faltam as strings: {missing}"

    return True, "OK"


def main():
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO: UI está otimizando ALGORITMOS?")
    print("=" * 80)

    # Verifica se estamos no diretório correto
    if not os.path.exists('src/web/app.py'):
        print("\n❌ ERRO: Execute este script do diretório projeto2_haversine/")
        print("   cd projeto2_haversine")
        print("   python scripts/check_ui_status.py")
        return False

    print("\n✅ Diretório correto: projeto2_haversine/")

    # Lista de verificações
    checks = []

    # 1. Verifica arquivo domains.py
    print("\n📋 Verificando arquivos...")

    check1 = os.path.exists('src/llm/domains.py')
    checks.append(("Arquivo domains.py existe", check1))
    print(f"  {'✅' if check1 else '❌'} src/llm/domains.py")

    # 2. Verifica arquivo variance_generator.py
    check2 = os.path.exists('src/llm/variance_generator.py')
    checks.append(("Arquivo variance_generator.py existe", check2))
    print(f"  {'✅' if check2 else '❌'} src/llm/variance_generator.py")

    # 3. Verifica conteúdo do app.py
    print("\n📝 Verificando conteúdo de src/web/app.py...")

    app_checks = [
        "from src.llm.domains import GADomains",
        "merged.update(new_params)",
        "GADomains.validate_params(merged)",
        "🧬 **Algoritmos Alterados:**",
        "algo_domains = GADomains.get_algorithmic_domains()",
        '"params": merged'
    ]

    check3, msg3 = check_file_content('src/web/app.py', app_checks)
    checks.append(("app.py tem código atualizado", check3))

    if check3:
        print(f"  ✅ Todas as 6 mudanças críticas encontradas")
    else:
        print(f"  ❌ {msg3}")
        print("\n  📌 Mudanças necessárias em app.py:")
        for search_str in app_checks:
            exists = search_str in open('src/web/app.py').read()
            print(f"     {'✅' if exists else '❌'} {search_str}")

    # 4. Verifica se há __pycache__ (cache pode interferir)
    print("\n🗑️  Verificando cache Python...")
    pycache_dirs = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))

    if pycache_dirs:
        print(f"  ⚠️  Encontrados {len(pycache_dirs)} diretórios __pycache__")
        print(f"     Recomendo limpar: find . -type d -name '__pycache__' -exec rm -rf {{}} + 2>/dev/null")
    else:
        print(f"  ✅ Nenhum cache encontrado")

    # 5. Testa importação
    print("\n🐍 Testando importações Python...")

    try:
        sys.path.insert(0, os.getcwd())
        from src.llm.domains import GADomains
        check5 = True
        print(f"  ✅ from src.llm.domains import GADomains")

        # Testa método
        algo_domains = GADomains.get_algorithmic_domains()
        num_algos = len(algo_domains)
        print(f"  ✅ GADomains.get_algorithmic_domains() retorna {num_algos} algoritmos")
        checks.append(("Importação GADomains funciona", True))

    except Exception as e:
        check5 = False
        print(f"  ❌ Erro ao importar: {e}")
        checks.append(("Importação GADomains funciona", False))

    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO:")
    print("=" * 80)

    all_pass = all(result for _, result in checks)

    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")

    print("=" * 80)

    if all_pass:
        print("\n🎉 SUCESSO! Todas as verificações passaram!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("   1. Se a UI está rodando, PARE (Ctrl+C)")
        print("   2. Reinicie: python src/web/app.py")
        print("   3. No navegador, force reload: Ctrl+Shift+R")
        print("   4. Vá para 🤖 Logistic LLM")
        print("   5. Execute otimização com 3 iterações")
        print("\n   Você DEVE ver a mensagem:")
        print('   "🧬 Algoritmos Alterados:"')
        print('   com mudanças em selection_method, crossover_method, mutation_method')
        print("\n" + "=" * 80)
        return True
    else:
        print("\n❌ FALHA! Algumas verificações não passaram.")
        print("\n🔧 AÇÕES CORRETIVAS:")

        if not checks[0][1]:  # domains.py
            print("\n   1. Arquivo domains.py não encontrado:")
            print("      - Verifique que existe: ls src/llm/domains.py")
            print("      - Se não existir, o arquivo não foi criado corretamente")

        if not checks[1][1]:  # variance_generator.py
            print("\n   2. Arquivo variance_generator.py não encontrado:")
            print("      - Verifique: ls src/llm/variance_generator.py")

        if not checks[2][1]:  # app.py
            print("\n   3. app.py não tem o código atualizado:")
            print("      - O arquivo src/web/app.py precisa ser editado")
            print("      - Verifique se as mudanças foram aplicadas corretamente")

        if not checks[3][1]:  # Importação
            print("\n   4. Importação falhou:")
            print("      - Há erro de sintaxe em domains.py")
            print("      - Execute: python -c 'from src.llm.domains import GADomains'")
            print("      - Corrija os erros antes de prosseguir")

        print("\n" + "=" * 80)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
