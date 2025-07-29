# 🍛 RescueBites

**RescueBites** is an intelligent web application that bridges the gap between surplus food and hunger by connecting **restaurants** with **NGOs**. Built with a modern stack and AI-driven insights, it reduces food waste and supports food-insecure communities through seamless coordination.

---

## 🚀 Features

- **Restaurant Dashboard:** Easily log surplus items and schedule donations  
- **NGO Portal:** View available meals, request pickups, and track deliveries  
- **Analytics:** Waste reduction metrics and impact reports  

---

## 💻 Tech Stack

| Layer         | Tools & Libraries                                      |
|---------------|--------------------------------------------------------|
| **Frontend**  | React (Vite), TypeScript, Tailwind CSS, Framer Motion  |
| **Routing**   | React Router v6                                        |
| **Icons**     | Lucide React                                           |
| **State Mgmt**| React Hooks                                            |
| **HTTP**      | Axios                                                  |
| **Backend**   | Node.js, Express.js                                    |
| **Database**  | Prisma ORM (SQLite)                                    |
| **Auth**      | JWT (stubbed for now)                                  |

---

## ⚙️ Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/RescueBites.git
cd RescueBites

# 2. Install dependencies
# frontend
cd frontend
npm install
# backend
cd ../backend
npm install

# 3. Create your .env file
cat > .env <<EOF
DATABASE_URL="file:./dev.db"
JWT_SECRET="your_jwt_secret"
EOF

# 4. Run migrations & seed
npx prisma migrate dev --name init
npx prisma db seed

# 5. Start development servers
# in one terminal
cd ../frontend && npm run dev
# in another terminal
cd ../backend && node server.cjs

