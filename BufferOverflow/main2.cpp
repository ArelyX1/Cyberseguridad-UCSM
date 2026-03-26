#include <iostream>
#include <cstring>
#include <cctype>
#include <cstdint>

using namespace std;

void dump_region(unsigned char* base, size_t size, const char* label) {
    cout << label << ": ";
    for (size_t i = 0; i < size; ++i) {
        unsigned char c = base[i];
        if (isprint(c)) cout << c;
        else cout << '.';
    }
    cout << " | ";
    for (size_t i = 0; i < size; ++i) {
        printf("%02x ", base[i]);
    }
    cout << endl;
}

int main() {
    char id[11];
    char nombre[21];
    int edad;

    printf("Direccion de id:     %p\n", (void*)id);
    printf("Direccion de nombre: %p\n", (void*)nombre);
    cout << "Ingrese el codigo (overflow con >11 chars):" << endl;
    cin >> id;
    //cin.getline(id, sizeof(id));
    cout << "Ingrese nombre:" << endl;
    cin >> nombre;
    //cin.getline(nombre, sizeof(nombre));
    cout << "Ingrese edad:" << endl;
    cin >> edad;

    size_t len_id = strlen(id);
    printf("id leido: %s (len=%zu)\n", id, len_id);
    printf("nombre leido: %s\n", nombre);

    uintptr_t id_addr = (uintptr_t)id;
    uintptr_t nombre_addr = (uintptr_t)nombre;
    uintptr_t overflow_start = id_addr + sizeof(id);

    printf("\n-- Direcciones --\n");
    printf("overflow_start = %p\n", (void*)overflow_start);
    printf("nombre_addr   = %p\n", (void*)nombre_addr);
    printf("nombre_end    = %p\n", (void*)(nombre_addr + sizeof(nombre)));

    size_t overflow_len = (len_id > sizeof(id)) ? (len_id - sizeof(id)) : 0;
    printf("overflow_len = %zu\n", overflow_len);

    if (overflow_len > 0) {
        dump_region((unsigned char*)(id - 8), 8 + sizeof(id) + 32, "stack around id");
    }

    cout << "Final -> nombre='" << nombre << "', id='" << id << "', edad=" << edad << endl;

    return 0;
}
