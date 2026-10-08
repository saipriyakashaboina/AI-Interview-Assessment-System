import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, Eye, EyeOff, User, ArrowRight, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const P = '#7C3AED';
const TEXT = '#1E1B4B';
const MUTED = '#6B7280';
const BORDER = '#E9E5F5';
const BG_ALT = '#F8F7FF';

const iconBox: React.CSSProperties = {
  position: 'absolute',
  left: 14,
  top: '50%',
  transform: 'translateY(-50%)',
  color: MUTED,
  pointerEvents: 'none',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 13,
  fontWeight: 600,
  color: TEXT,
  marginBottom: 8,
};

const emptyForm = {
  email: '',
  password: '',
  full_name: '',
};

export default function LoginPage() {
  const { login, register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const mode = searchParams.get('mode');
  const isLogin = mode !== 'register';

  useEffect(() => {
    if (!mode) {
      setSearchParams({ mode: 'signin' }, { replace: true });
    }
  }, [mode, setSearchParams]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const setIsLogin = (value: boolean) => {
    setSearchParams(
      { mode: value ? 'signin' : 'register' },
      { replace: true }
    );
  };

  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    setForm(emptyForm);
    setError('');
  }, [isLogin]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(form.email, form.password);
      } else {
        await register(form.email, form.password, form.full_name);
      }
    } catch (err: unknown) {
      const axiosErr = err as {
        response?: {
          data?: {
            detail?: string;
          };
        };
        message?: string;
      };

      const message =
        axiosErr.response?.data?.detail ??
        axiosErr.message ??
        'Something went wrong';

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const toggleBtn = (active: boolean): React.CSSProperties => ({
    flex: 1,
    padding: '11px 0',
    border: 'none',
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all .2s',
    background: active ? P : 'transparent',
    color: active ? '#fff' : MUTED,
    boxShadow: active ? '0 2px 8px rgba(124,58,237,.3)' : 'none',
  });

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '90px 20px 40px',
        background: '#F8F7FF',
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          width: '100%',
          maxWidth: 440,
        }}
      >
        <div
          style={{
            background: '#fff',
            border: `1px solid ${BORDER}`,
            borderTop: `3px solid ${P}`,
            borderRadius: 12,
            boxShadow: '0 4px 24px rgba(0,0,0,.06)',
            padding: '36px 32px',
          }}
        >
          <h2
            style={{
              fontFamily: 'Poppins, sans-serif',
              fontSize: 22,
              fontWeight: 700,
              color: TEXT,
              textAlign: 'center',
              marginBottom: 6,
            }}
          >
            {isLogin ? 'Welcome back' : 'Create account'}
          </h2>

          {isLogin && (
            <p
              style={{
                fontSize: 14,
                color: MUTED,
                textAlign: 'center',
                marginBottom: 28,
              }}
            >
              Sign in to continue your journey
            </p>
          )}

          <div
            style={{
              display: 'flex',
              background: BG_ALT,
              padding: 4,
              marginBottom: 24,
              border: `1px solid ${BORDER}`,
            }}
          >
            <button
              onClick={() => setIsLogin(true)}
              style={toggleBtn(isLogin)}
            >
              Sign In
            </button>

            <button
              onClick={() => setIsLogin(false)}
              style={toggleBtn(!isLogin)}
            >
              Register
            </button>
          </div>

          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                style={{
                  background: 'rgba(239,68,68,.08)',
                  border: '1px solid rgba(239,68,68,.25)',
                  color: '#ef4444',
                  padding: '12px 16px',
                  fontSize: 13,
                  marginBottom: 20,
                }}
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <form
            onSubmit={handleSubmit}
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 18,
            }}
          >
            <AnimatePresence mode="wait">
              {!isLogin && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <label style={labelStyle}>Full Name</label>

                  <div style={{ position: 'relative' }}>
                    <User size={17} style={iconBox} />

                    <input
                      type="text"
                      value={form.full_name}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          full_name: e.target.value,
                        })
                      }
                      placeholder="Your full name"
                      className="input"
                      style={{ paddingLeft: 42 }}
                      required={!isLogin}
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label style={labelStyle}>Email</label>

              <div style={{ position: 'relative' }}>
                <Mail size={17} style={iconBox} />

                <input
                  type="email"
                  value={form.email}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      email: e.target.value,
                    })
                  }
                  placeholder="your@email.com"
                  className="input"
                  style={{ paddingLeft: 42 }}
                  required
                />
              </div>
            </div>

            <div>
              <label style={labelStyle}>Password</label>

              <div style={{ position: 'relative' }}>
                <Lock size={17} style={iconBox} />

                <input
                  type={showPw ? 'text' : 'password'}
                  value={form.password}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      password: e.target.value,
                    })
                  }
                  placeholder="••••••••"
                  className="input"
                  style={{
                    paddingLeft: 42,
                    paddingRight: 42,
                  }}
                  required
                />

                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  style={{
                    position: 'absolute',
                    right: 14,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: MUTED,
                  }}
                >
                  {showPw ? (
                    <EyeOff size={17} />
                  ) : (
                    <Eye size={17} />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 10,
                width: '100%',
                padding: '12px 0',
                border: 'none',
                background: loading ? '#C4B5FD' : P,
                color: '#fff',
                fontSize: 14,
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                marginTop: 4,
                transition: 'background .2s',
              }}
            >
              {loading ? (
                <Loader2 className="animate-spin" size={18} />
              ) : (
                <>
                  {isLogin ? 'Sign In' : 'Create Account'}
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}