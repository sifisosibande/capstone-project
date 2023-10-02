import express from 'express';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static('public'));

// Function to generate a verification token
function generateVerificationToken() {
    return uuidv4();
}

async function initializeDatabase() {
    const db = await open({
        filename: './db/data_plan.db',
        driver: sqlite3.Database,
    });

    await db.migrate();
    return db;
}

// Registration endpoint
app.post('/api/register', async (req, res) => {
    const { username, password, email } = req.body;

    try {
        const db = await initializeDatabase();

        // Check if the username or email already exists in the database
        const existingUser = await db.get('SELECT * FROM users WHERE username = ? OR email = ?', [username, email]);

        if (existingUser) {
            return res.status(409).json({ error: 'Username or email already exists' });
        }

        // Hash the password before storing it
        const hashedPassword = await bcrypt.hash(password, 10);

        // Generate a verification token
        const verificationToken = generateVerificationToken();

        // Insert the user data into the 'users' table, including the verification token
        const result = await db.run(
            'INSERT INTO users (username, password, email, verification_token) VALUES (?, ?, ?, ?)',
            [username, hashedPassword, email, verificationToken]
        );

        if (result.lastID) {
            // Send a verification email (you can implement this part)
            return res.status(201).json({ message: 'User registered successfully. Check your email for verification.' });
        } else {
            return res.status(500).json({ error: 'Failed to register user' });
        }
    } catch (error) {
        console.error(error.message);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

// Inside your /api/login endpoint (replace with your authentication logic)

// Protected route (home page)
app.get('/home', (req, res) => {
    // Get the directory name using __dirname
    const __dirname = path.resolve();

    // Construct the correct file path with the root directory
    const filePath = path.join(__dirname, 'public', 'home.html');

    // Serve the home page for authenticated users
    res.sendFile(filePath);
});

// Logout endpoint
app.get('/logout', (req, res) => {
    // Implement logout logic if needed
    // For simplicity, we'll just redirect to the login page
    res.redirect('/');
});

// Account deletion endpoint
app.delete('/api/delete-account/:id', async (req, res) => {
    try {
        const db = await initializeDatabase();
console.log(req.params);
        // You should have a way to identify the user, such as their user ID or username
        const userId = req.params.id; // Replace with the correct way to get the user ID

        if (!userId) {
            return res.status(401).json({ error: 'Unauthorized' });
        }

        // Delete the user's account and data from the database
        await db.run('DELETE FROM users WHERE id = ?', userId);

        // You may want to also perform additional cleanup, such as deleting related data in other tables

        return res.status(200).json({ message: 'Account deleted successfully' });
    } catch (error) {
        console.error(error.message);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
