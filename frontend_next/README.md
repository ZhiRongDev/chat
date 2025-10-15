# ChatGPT-like Application (Next.js)

A modern ChatGPT-like chat application built with Next.js 14, TypeScript, and Tailwind CSS. This application features a clean interface with chat history management, streaming responses, and persistent storage using IndexedDB.

## Features

- **Real-time Chat**: Send messages and receive streaming responses from the backend API
- **Chat History**: Automatically save and load chat conversations
- **IndexedDB Storage**: Persistent client-side storage for chat history
- **Responsive Design**: Clean, mobile-friendly interface similar to ChatGPT
- **Modal System**: Login, Register, and Settings modals
- **Sidebar Navigation**: Collapsible sidebar with chat history
- **Dark Theme Sidebar**: Professional dark-themed sidebar navigation

## Tech Stack

- **Next.js 14**: React framework with App Router
- **React 18**: UI library
- **TypeScript**: Type-safe development
- **Tailwind CSS 3**: Utility-first CSS framework
- **IndexedDB**: Client-side database for chat storage

## Project Structure

```
frontend_next/
├── app/
│   ├── page.tsx          # Main chat page component
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── lib/
│   └── chatStorage.ts    # IndexedDB utility for chat history
├── .env.local            # Environment variables
└── package.json
```

## Getting Started

### Prerequisites

- Node.js 20.x or 22.x
- Backend API running on `http://localhost:5000` (or configure via environment variable)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create `.env.local` file (already created):

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## API Integration

The application expects a backend API endpoint at `/api/v1/chat` that:

- Accepts POST requests with JSON body: `{ message: string }`
- Returns streaming responses
- Example backend endpoint: `http://localhost:5000/api/v1/chat`

## Features in Detail

### Chat Storage

- Automatically saves chat conversations to IndexedDB
- Loads the most recent chat on app start
- Each chat has a unique ID and title (based on first user message)
- Sort chats by creation date (newest first)

### Chat History Management

- **New Chat**: Start a fresh conversation
- **Load Chat**: Click on any chat in the sidebar to load it
- **Delete Chat**: Hover over a chat item and click the delete icon

### Streaming Responses

The application supports streaming responses from the backend API, displaying the bot's reply character by character as it's received.

### Modal System

- **Login Modal**: User authentication (placeholder)
- **Register Modal**: User registration (placeholder)
- **Settings Modal**: App preferences (placeholder)

## Customization

### Styling

The app uses Tailwind CSS for styling. Modify classes in `app/page.tsx` to customize the appearance.

### API Endpoint

Change the API endpoint in `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-api-url.com
```

### Chat Storage

Modify `lib/chatStorage.ts` to customize:
- Database name and version
- Chat title generation logic
- Storage behavior

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari

Note: IndexedDB must be supported by the browser.

## Known Issues

- Modal authentication is placeholder functionality
- No actual user authentication system integrated yet

## Future Enhancements

- [ ] User authentication integration
- [ ] Markdown rendering for bot responses
- [ ] Code syntax highlighting
- [ ] Export chat history
- [ ] Search chat history
- [ ] Dark/light mode toggle
- [ ] Voice input support

## License

MIT

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
