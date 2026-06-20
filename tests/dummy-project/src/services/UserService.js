// tests/dummy-project/src/services/UserService.js
const User = require('../models/User');

class UserService {
  static async createUser(data) {
    // Side effect: check if email is taken
    const existing = await User.findOne({ where: { email: data.email } });
    if (existing) {
      throw new Error("Email already taken");
    }
    
    // Save to database
    const newUser = await User.create({
      username: data.username,
      email: data.email,
      password: data.password // In production, hash this!
    });
    
    return newUser;
  }

  static async updateProfile(id, data) {
    const user = await User.findByPk(id);
    if (!user) {
      throw new Error("User not found");
    }
    
    await user.update({
      displayName: data.displayName,
      bio: data.bio
    });
    
    return user;
  }

  static async getUser(id) {
    return await User.findByPk(id);
  }
}

module.exports = UserService;
