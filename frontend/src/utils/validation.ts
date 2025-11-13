import * as yup from 'yup'

/**
 * Validation schemas using Yup
 */

// Username validation schema (supports both username and email formats)
export const usernameSchema = yup
  .string()
  .required('Username is required')
  .min(3, 'Username must be at least 3 characters')
  .max(100, 'Username must not exceed 100 characters')
  .test('username-or-email', 'Please enter a valid username or email address', (value) => {
    if (!value) return false
    // Check if it's a valid email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    // Check if it's a valid username (alphanumeric with underscores, hyphens, and dots)
    const usernameRegex = /^[a-zA-Z0-9_.-]+$/

    return emailRegex.test(value) || usernameRegex.test(value)
  })

// Email validation schema
export const emailSchema = yup
  .string()
  .required('Email is required')
  .email('Please enter a valid email address')
  .max(100, 'Email must not exceed 100 characters')

// Password validation schema
export const passwordSchema = yup
  .string()
  .required('Password is required')
  .min(6, 'Password must be at least 6 characters')
  .max(100, 'Password must not exceed 100 characters')

// Confirm password validation (requires context)
export const confirmPasswordSchema = (passwordFieldName: string = 'password') =>
  yup
    .string()
    .required('Please confirm your password')
    .oneOf([yup.ref(passwordFieldName)], 'Passwords do not match')

/**
 * Validation rules for VeeValidate
 */
export const validationRules = {
  username: (value: string) => {
    try {
      usernameSchema.validateSync(value)
      return true
    } catch (error: any) {
      return error.message
    }
  },

  // Alias for username that accepts email format
  usernameOrEmail: (value: string) => {
    try {
      usernameSchema.validateSync(value)
      return true
    } catch (error: any) {
      return error.message
    }
  },

  email: (value: string) => {
    try {
      emailSchema.validateSync(value)
      return true
    } catch (error: any) {
      return error.message
    }
  },

  password: (value: string) => {
    try {
      passwordSchema.validateSync(value)
      return true
    } catch (error: any) {
      return error.message
    }
  },

  confirmPassword: (value: string, [target]: [string]) => {
    if (!value) {
      return 'Please confirm your password'
    }
    if (value !== target) {
      return 'Passwords do not match'
    }
    return true
  },

  required: (value: any) => {
    if (!value || (typeof value === 'string' && !value.trim())) {
      return 'This field is required'
    }
    return true
  },
}

/**
 * Custom validation utilities
 */
export const validateField = async (
  schema: yup.Schema,
  value: any
): Promise<{ valid: boolean; error?: string }> => {
  try {
    await schema.validate(value)
    return { valid: true }
  } catch (error: any) {
    return { valid: false, error: error.message }
  }
}

/**
 * Full form validation schemas
 */
export const loginSchema = yup.object({
  username: usernameSchema,
  password: passwordSchema,
})

export const registerSchema = yup.object({
  username: usernameSchema,
  password: passwordSchema,
  confirmPassword: confirmPasswordSchema('password'),
})

export const resetPasswordSchema = yup.object({
  newPassword: passwordSchema,
  confirmPassword: confirmPasswordSchema('newPassword'),
})

export const forgotPasswordSchema = yup.object({
  username: usernameSchema,
})
