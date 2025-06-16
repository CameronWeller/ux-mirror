const CryptoJS = require('crypto-js');

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || 'default-32-character-encryption-key';

// Ensure key is exactly 32 characters
const getKey = () => {
  const key = ENCRYPTION_KEY.padEnd(32, '0').substring(0, 32);
  return key;
};

const encrypt = (text) => {
  if (!text) return null;
  
  try {
    const encrypted = CryptoJS.AES.encrypt(text, getKey()).toString();
    return encrypted;
  } catch (error) {
    console.error('Encryption error:', error);
    throw new Error('Failed to encrypt data');
  }
};

const decrypt = (encryptedText) => {
  if (!encryptedText) return null;
  
  try {
    const decrypted = CryptoJS.AES.decrypt(encryptedText, getKey());
    const decryptedText = decrypted.toString(CryptoJS.enc.Utf8);
    
    if (!decryptedText) {
      throw new Error('Failed to decrypt - invalid key or corrupted data');
    }
    
    return decryptedText;
  } catch (error) {
    console.error('Decryption error:', error);
    throw new Error('Failed to decrypt data');
  }
};

// Generate a random string for backup codes
const generateBackupCode = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let code = '';
  
  for (let i = 0; i < 8; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
    if (i === 3) code += '-'; // Format: XXXX-XXXX
  }
  
  return code;
};

// Generate multiple backup codes
const generateBackupCodes = (count = 10) => {
  const codes = [];
  const usedCodes = new Set();
  
  while (codes.length < count) {
    const code = generateBackupCode();
    if (!usedCodes.has(code)) {
      usedCodes.add(code);
      codes.push(code);
    }
  }
  
  return codes;
};

module.exports = {
  encrypt,
  decrypt,
  generateBackupCode,
  generateBackupCodes
};