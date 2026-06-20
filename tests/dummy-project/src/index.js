// tests/dummy-project/src/index.js
const express = require('express');
const { z } = require('zod');
const UserService = require('./services/UserService');

const app = express();
app.use(express.json());

// Zod schemas for request validation
const CreateUserSchema = z.object({
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(6)
});

const UpdateProfileSchema = z.object({
  displayName: z.string().optional(),
  bio: z.string().max(200).optional()
});

// Express route handling
app.post('/api/users', async (req, res) => {
  try {
    const validatedData = CreateUserSchema.parse(req.body);
    const user = await UserService.createUser(validatedData);
    return res.status(201).json(user);
  } catch (error) {
    return res.status(400).json({ error: error.message });
  }
});

app.put('/api/users/:id', async (req, res) => {
  try {
    const validatedData = UpdateProfileSchema.parse(req.body);
    const updatedUser = await UserService.updateProfile(req.params.id, validatedData);
    return res.json(updatedUser);
  } catch (error) {
    return res.status(400).json({ error: error.message });
  }
});

app.get('/api/users/:id', async (req, res) => {
  const user = await UserService.getUser(req.params.id);
  if (!user) return res.status(404).send('User not found');
  return res.json(user);
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
