# SIPROSA MES - Frontend

Frontend desarrollado con Next.js 14 para el Sistema de Gestión de Manufactura de SIPROSA.

## 🚀 Tecnologías

- **Next.js 14** - Framework React con App Router
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos y diseño
- **Zustand** - Gestión de estado global
- **TanStack Query** - Manejo de datos de API
- **React Hook Form** - Formularios y validación
- **Lucide React** - Iconos

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Construir para producción
npm run build

# Iniciar servidor de producción
npm start
```

## 🌐 Desarrollo

El frontend se ejecuta en `http://localhost:3000` y se conecta automáticamente con el backend en `http://localhost:8000`.

## 📁 Estructura

```
src/
├── app/                 # App Router de Next.js
├── components/          # Componentes reutilizables
│   └── ui/             # Componentes base de UI
├── lib/                # Utilidades y configuración
├── stores/             # Stores de Zustand
├── types/              # Definiciones de tipos TypeScript
└── utils/              # Funciones auxiliares
```

## 🎯 Características

- ✅ Dashboard con métricas en tiempo real
- ✅ Gestión de producción (lotes, etapas, controles)
- ✅ Sistema de mantenimiento
- ✅ Gestión de inventario FEFO
- ✅ Sistema de incidentes y acciones correctivas
- ✅ Auditoría completa de operaciones
- ✅ Autenticación JWT integrada
