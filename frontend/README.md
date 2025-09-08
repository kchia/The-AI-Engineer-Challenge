# 🚀 AI Chat Assistant Frontend

A **stunning**, modern chat interface that'll make your jaw drop! Built with Next.js and Tailwind CSS, this beauty is designed to work seamlessly with the FastAPI backend. Get ready to chat with AI like never before! ✨

## ✨ What Makes This Awesome

- 🤖 **Real-time Magic**: Watch AI responses stream in real-time - it's like having a conversation with the future!
- 🎨 **4 Gorgeous Themes**: Pick your vibe from Modern Blue, Corporate Gray, Tech Purple, or go wild with Dark Mode
- 🌙 **Dark Mode Mastery**: Toggle between light and dark themes instantly - your eyes will thank you!
- 📱 **Responsive Perfection**: Looks absolutely stunning on mobile, tablet, and desktop (seriously, try it!)
- 🔐 **Fort Knox Security**: Your API keys are stored locally and never leave your device
- ⚡ **Lightning Fast**: Built with Next.js 14 and TypeScript - it's like greased lightning!
- ♿ **Accessible AF**: WCAG compliant with keyboard navigation - everyone deserves great UX!

## 🚀 Get Started in 3 Easy Steps!

### What You'll Need

- **Node.js 18+** (the magic runtime)
- **npm** (your package manager buddy)
- **OpenAI API key** (your golden ticket to AI paradise)
- **FastAPI backend** running on `http://localhost:8000` (the brain behind the beauty)

### Let's Do This! 🎯

1. **Install the good stuff**:

```bash
npm install
```

2. **Fire up the dev server**:

```bash
npm run dev
```

3. **Open your browser** and go to [http://localhost:3000](http://localhost:3000) - prepare to be amazed! 🤩

### First Time Setup

1. **🔑 API Key Magic**: Click that sexy settings button (⚙️) and enter your OpenAI API key
2. **🎨 Pick Your Style**: Choose from Modern Blue, Corporate Gray, or Tech Purple themes
3. **🌙 Dark Mode Toggle**: Switch between light and dark themes - it's like having two apps in one!

## 🎮 How to Use This Beauty

1. **🔑 Enter Your API Key**: Head to settings and add your OpenAI API key (it's like giving the app superpowers!)
2. **💬 Start the Magic**: Type a message and hit Enter - watch the AI respond in real-time!
3. **✨ Streaming Awesomeness**: Responses appear word by word - it's like watching AI think out loud!
4. **🎨 Theme Customization**: Switch themes and toggle dark mode anytime - make it yours!
5. **🧹 Fresh Start**: Hit "Clear Chat" when you want to start a new conversation

## 🔌 API Integration (The Technical Stuff)

This frontend is a perfect match for the FastAPI backend! It connects to `http://localhost:8000` and expects:

- **Health Check**: `GET /api/health` (making sure the backend is alive and kicking!)
- **Chat Endpoint**: `POST /api/chat` with streaming response (the magic happens here!)

### Environment Variables

Want to customize the API URL? Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

_Pro tip: This is super useful for different environments!_

## 📁 Project Structure (The Blueprint)

```
frontend/
├── app/
│   ├── globals.css          # 🎨 Global styles with gorgeous color themes
│   ├── layout.tsx           # 🏗️ Root layout with theme provider magic
│   └── page.tsx             # 🏠 Main page with the chat interface
├── components/
│   ├── ChatInterface.tsx    # 💬 The main chat component (the star of the show!)
│   ├── MessageBubble.tsx    # 💭 Individual message display (so pretty!)
│   ├── MessageInput.tsx     # ⌨️ Message input with auto-resize (smart!)
│   ├── ApiKeyInput.tsx      # 🔐 Secure API key input (Fort Knox level!)
│   └── ThemeSelector.tsx    # 🎨 Theme and dark mode controls (the style master!)
├── lib/
│   ├── api.ts               # 🔌 API client for backend integration
│   └── theme-context.tsx    # 🌈 Theme management context (the color wizard!)
└── README.md                # 📖 This beautiful file you're reading!
```

## 🎨 Available Themes (Pick Your Vibe!)

### 1. Modern Blue (Default) 🔵

- **Primary**: Blue-600 (#2563eb) - that perfect corporate blue
- **Vibe**: Clean, professional, and trustworthy
- **Perfect for**: Corporate apps, SaaS platforms, and serious business

### 2. Corporate Gray 🏢

- **Primary**: Gray-700 (#374151) - sophisticated and sleek
- **Vibe**: Conservative, business-focused, and reliable
- **Perfect for**: Enterprise applications and professional environments

### 3. Tech Purple 💜

- **Primary**: Violet-600 (#7c3aed) - bold and innovative
- **Vibe**: Modern, tech-forward, and creative
- **Perfect for**: Innovative apps, creative tools, and tech startups

### 4. Dark Mode 🌙

- **Available for**: All themes (yes, ALL of them!)
- **Vibe**: Easy on the eyes, modern, and sleek
- **Perfect for**: Late-night coding sessions and looking cool 😎

## 🛠️ Development (For the Code Wizards)

### Available Scripts

- `npm run dev` - 🚀 Start development server (the magic begins!)
- `npm run build` - 🏗️ Build for production (make it production-ready!)
- `npm run start` - 🌟 Start production server (showtime!)
- `npm run lint` - 🔍 Run ESLint (keep that code clean!)

### Key Technologies (The Dream Team)

- **Next.js 14**: React framework with App Router (the foundation of greatness!)
- **TypeScript**: Type-safe development (because bugs are not our friends!)
- **Tailwind CSS v3.4**: Utility-first CSS framework (the styling wizard!)
- **Lucide React**: Beautiful icons (making everything look gorgeous!)
- **Radix UI**: Accessible component primitives (inclusion is everything!)

## 🚀 Deployment (Time to Go Live!)

This frontend is designed to work beautifully with Vercel deployment:

1. **🏗️ Build the project**: `npm run build` (make it production-ready!)
2. **🌐 Deploy to Vercel**: Connect your GitHub repository (one-click magic!)
3. **⚙️ Configure environment**: Set `NEXT_PUBLIC_API_URL` to your backend URL

The Vercel configuration in the root directory handles routing between frontend and API like a pro!

_Pro tip: Vercel makes deployment so easy, it's almost cheating! 😉_

## 🆘 Troubleshooting (When Things Go Wrong)

### Common Issues (And How to Fix Them!)

1. **🔌 API Connection Failed**

   - Make sure the FastAPI backend is running on port 8000 (it's the brain!)
   - Check that CORS is properly configured (cross-origin requests need love too!)
   - Verify your API key is correct (double-check that golden ticket!)

2. **🎨 Theme Not Applying**

   - Clear browser cache and reload (sometimes browsers are stubborn!)
   - Check browser developer tools for CSS errors (the console is your friend!)

3. **💬 Messages Not Streaming**
   - Verify the backend is returning streaming responses (the magic needs to flow!)
   - Check network tab for API errors (follow the data trail!)

### Browser Support (The Cool Kids)

- **Chrome 90+** (the speed demon!)
- **Firefox 88+** (the privacy champion!)
- **Safari 14+** (the Apple way!)
- **Edge 90+** (the Microsoft makeover!)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the AI Engineer Challenge and follows the same license terms.
