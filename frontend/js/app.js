/**
 * NeoBank & Chrome Slots - Main Vue.js Application
 */

const { createApp } = Vue;

const API_BASE = window.location.origin;

createApp({
    data() {
        return {
            loading: true,
            authMode: 'login',
            currentView: 'bank',
            user: null,
            token: null,
            error: null,
            
            // Forms
            loginForm: {
                character_name: '',
                password: ''
            },
            registerForm: {
                character_name: '',
                password: '',
                faction: ''
            },
            transferForm: {
                to_account: '',
                amount: '',
                memo: ''
            },
            
            // Banking
            transactions: [],
            searchQuery: '',
            searchTimeout: null,
            
            // Casino
            selectedGame: 'glitch',
            spinning: false,
            glitchReels: ['💀', '01', '🔌'],
            glitchBet: 10,
            starlightGrid: [
                ['🚀', '🗺️', '🔫', '💎', '⭐'],
                ['🗺️', '🔫', '💎', '⭐', '🌀'],
                ['🔫', '💎', '⭐', '🌀', '🚀']
            ],
            starlightBet: 5,
            lastResult: null,
            showPaytable: false,
            
            // Profile
            profileEmojis: ['😎', '🤖', '👾', '🦾', '💀', '🔥', '⚡', '💎', '🌟', '🎮', '🎯', '🚀', '🔫', '💊', '🌀', '👁️'],
            passwordForm: {
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
            },
            
            // Admin
            adminSearch: '',
            searchResults: [],
            adjustingUser: null,
            adjustAmount: 0,
            adjustReason: '',
            apiKeys: [],
            casinoGames: [],
            factions: [],
            factionCreditsModal: null,
            factionCreditsAmount: 0,
            factionCreditsReason: '',
            newFactionName: '',
            newFactionDescription: '',
            
            // Notifications
            toasts: []
        };
    },
    
    mounted() {
        // Check for saved token
        const savedToken = localStorage.getItem('neobank_token');
        if (savedToken) {
            this.token = savedToken;
            this.loadUserData();
        } else {
            this.loading = false;
        }
    },
    
    methods: {
        // ============ Authentication ============
        async login() {
            try {
                this.error = null;
                const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.loginForm)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Login failed');
                }
                
                this.token = data.access_token;
                this.user = data.user;
                localStorage.setItem('neobank_token', this.token);
                
                this.showToast('Access granted', 'success');
                await this.loadUserData();
                
            } catch (err) {
                this.error = err.message;
                this.showToast(err.message, 'error');
            }
        },
        
        async register() {
            try {
                this.error = null;
                const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.registerForm)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Registration failed');
                }
                
                this.showToast('Account created! Please login.', 'success');
                this.authMode = 'login';
                this.loginForm.character_name = this.registerForm.character_name;
                
            } catch (err) {
                this.error = err.message;
                this.showToast(err.message, 'error');
            }
        },
        
        logout() {
            this.user = null;
            this.token = null;
            localStorage.removeItem('neobank_token');
            this.showToast('Disconnected', 'success');
        },
        
        async loadUserData() {
            try {
                const response = await fetch(`${API_BASE}/api/v1/account`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                
                if (!response.ok) {
                    throw new Error('Session expired');
                }
                
                const data = await response.json();
                this.user = data.account;
                await this.loadTransactions();
                
            } catch (err) {
                this.logout();
                this.showToast('Session expired, please login again', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        // ============ Banking ============
        async loadTransactions(limit = 10) {
            try {
                const response = await fetch(`${API_BASE}/api/v1/account/transactions?limit=${limit}`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                
                const data = await response.json();
                this.transactions = data.transactions;
                
            } catch (err) {
                console.error('Failed to load transactions:', err);
            }
        },
        
        async transfer() {
            try {
                const response = await fetch(`${API_BASE}/api/v1/transactions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify(this.transferForm)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Transfer failed');
                }
                
                this.user.balance = data.new_balance;
                this.showToast('Transfer successful', 'success');
                
                // Reset form
                this.transferForm = { to_account: '', amount: '', memo: '' };
                
                // Reload transactions
                await this.loadTransactions();
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        async searchTransactions() {
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }
            
            if (!this.searchQuery.trim()) {
                await this.loadTransactions();
                return;
            }
            
            this.searchTimeout = setTimeout(async () => {
                try {
                    const response = await fetch(
                        `${API_BASE}/api/v1/account/transactions/search?q=${encodeURIComponent(this.searchQuery)}`,
                        { headers: { 'Authorization': `Bearer ${this.token}` } }
                    );
                    
                    const data = await response.json();
                    this.transactions = data.transactions;
                    
                } catch (err) {
                    console.error('Search failed:', err);
                }
            }, 500);
        },
        
        // ============ Casino ============
        increaseBet(game) {
            if (game === 'glitch') {
                this.glitchBet = Math.min(this.glitchBet + 10, 1000);
            } else {
                this.starlightBet = Math.min(this.starlightBet + 5, 500);
            }
        },
        
        decreaseBet(game) {
            if (game === 'glitch') {
                this.glitchBet = Math.max(this.glitchBet - 10, 10);
            } else {
                this.starlightBet = Math.max(this.starlightBet - 5, 5);
            }
        },
        
        async spinGlitch() {
            if (this.spinning) return;
            
            this.spinning = true;
            this.lastResult = null;
            
            // Spinning animation
            const spinDuration = 2000;
            const spinInterval = setInterval(() => {
                this.glitchReels = [
                    this.randomSymbol(['💀', '01', '🔌', '㊙️', '🏢']),
                    this.randomSymbol(['💀', '01', '🔌', '㊙️', '🏢']),
                    this.randomSymbol(['💀', '01', '🔌', '㊙️', '🏢'])
                ];
            }, 100);
            
            try {
                const response = await fetch(`${API_BASE}/api/v1/casino/glitch-grid/spin`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({ bet_amount: this.glitchBet })
                });
                
                const data = await response.json();
                
                setTimeout(() => {
                    clearInterval(spinInterval);
                    
                    if (!response.ok) {
                        throw new Error(data.error || 'Spin failed');
                    }
                    
                    this.glitchReels = data.reels;
                    this.lastResult = data;
                    this.user.balance = data.balance;
                    
                    if (data.win_amount > 0) {
                        this.showToast(`You won ¤${data.win_amount}!`, 'success');
                    }
                    
                    this.spinning = false;
                }, spinDuration);
                
            } catch (err) {
                clearInterval(spinInterval);
                this.spinning = false;
                this.showToast(err.message, 'error');
            }
        },
        
        async spinStarlight() {
            if (this.spinning) return;
            
            this.spinning = true;
            this.lastResult = null;
            
            // Spinning animation
            const spinDuration = 2500;
            const spinInterval = setInterval(() => {
                this.starlightGrid = [
                    this.randomRow(),
                    this.randomRow(),
                    this.randomRow()
                ];
            }, 100);
            
            try {
                const response = await fetch(`${API_BASE}/api/v1/casino/starlight-smuggler/spin`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({ bet_amount: this.starlightBet })
                });
                
                const data = await response.json();
                
                setTimeout(() => {
                    clearInterval(spinInterval);
                    
                    if (!response.ok) {
                        throw new Error(data.error || 'Spin failed');
                    }
                    
                    this.starlightGrid = data.grid;
                    this.lastResult = data;
                    this.user.balance = data.balance;
                    
                    if (data.win_amount > 0) {
                        this.showToast(`You won ¤${data.win_amount}!`, 'success');
                    }
                    
                    this.spinning = false;
                }, spinDuration);
                
            } catch (err) {
                clearInterval(spinInterval);
                this.spinning = false;
                this.showToast(err.message, 'error');
            }
        },
        
        randomSymbol(symbols) {
            return symbols[Math.floor(Math.random() * symbols.length)];
        },
        
        randomRow() {
            const symbols = ['🚀', '🗺️', '🔫', '💎', '🌀', '⭐'];
            return Array(5).fill().map(() => this.randomSymbol(symbols));
        },
        
        // ============ Admin ============
        async searchUsers() {
            if (!this.adminSearch.trim()) {
                this.searchResults = [];
                return;
            }
            
            try {
                const response = await fetch(
                    `${API_BASE}/api/admin/users/search?q=${encodeURIComponent(this.adminSearch)}`,
                    { headers: { 'Authorization': `Bearer ${this.token}` } }
                );
                
                const data = await response.json();
                this.searchResults = data.users || [];
                
            } catch (err) {
                console.error('Search failed:', err);
            }
        },
        
        openAdjustBalance(user) {
            this.adjustingUser = user;
            this.adjustAmount = 0;
            this.adjustReason = '';
        },
        
        async adjustBalance() {
            try {
                const response = await fetch(
                    `${API_BASE}/api/admin/users/${this.adjustingUser.account_number}/adjust-balance`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${this.token}`
                        },
                        body: JSON.stringify({
                            amount: this.adjustAmount,
                            reason: this.adjustReason
                        })
                    }
                );
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Adjustment failed');
                }
                
                this.showToast('Balance adjusted successfully', 'success');
                this.adjustingUser = null;
                await this.searchUsers();
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        async toggleAdminStatus(user) {
            // Prevent toggling own admin status
            if (user.account_number === this.user.account_number) {
                this.showToast('Cannot modify your own admin status', 'error');
                return;
            }
            
            const action = user.is_admin ? 'revoke admin privileges from' : 'grant admin privileges to';
            const actionShort = user.is_admin ? 'revoke' : 'grant';
            
            if (!confirm(`${action} ${user.character_name}?`)) {
                // Revert checkbox state if cancelled
                await this.searchUsers();
                return;
            }
            
            try {
                const response = await fetch(
                    `${API_BASE}/api/admin/users/${user.account_number}/toggle-admin`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${this.token}`
                        }
                    }
                );
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to update admin status');
                }
                
                this.showToast(`✓ ${data.message}`, 'success');
                await this.searchUsers();
                
            } catch (err) {
                this.showToast(err.message, 'error');
                // Revert on error
                await this.searchUsers();
            }
        },
        
        async loadApiKeys() {
            try {
                const response = await fetch(`${API_BASE}/api/admin/api-keys`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                
                const data = await response.json();
                this.apiKeys = data.api_keys || [];
                
            } catch (err) {
                console.error('Failed to load API keys:', err);
            }
        },
        
        async createApiKey() {
            const description = prompt('Enter API key description:');
            if (!description) return;
            
            try {
                const response = await fetch(`${API_BASE}/api/admin/api-keys`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({ description })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to create API key');
                }
                
                this.showToast('API key created', 'success');
                await this.loadApiKeys();
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        async revokeApiKey(keyId) {
            if (!confirm('Revoke this API key?')) return;
            
            try {
                const response = await fetch(`${API_BASE}/api/admin/api-keys/${keyId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to revoke API key');
                }
                
                this.showToast('API key revoked', 'success');
                await this.loadApiKeys();
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        async loadCasinoGames() {
            try {
                const response = await fetch(`${API_BASE}/api/admin/casino/config`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                
                const data = await response.json();
                this.casinoGames = data.games || [];
                
            } catch (err) {
                console.error('Failed to load casino games:', err);
            }
        },
        
        async updateGameConfig(game) {
            try {
                const response = await fetch(`${API_BASE}/api/admin/casino/config/${game.game_name}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({
                        is_enabled: game.is_enabled,
                        payout_percentage: game.payout_percentage
                    })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to update game config');
                }
                
                this.showToast('Game configuration updated', 'success');
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        // ============ Profile Management ============
        selectProfilePicture(emoji) {
            this.user.profile_picture = emoji;
        },
        
        async updateProfile() {
            try {
                const response = await fetch(`${API_BASE}/api/v1/account/profile`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({
                        faction: this.user.faction,
                        profile_picture: this.user.profile_picture
                    })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to update profile');
                }
                
                this.showToast('Profile updated successfully', 'success');
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        async changePassword() {
            try {
                // Validate passwords match
                if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
                    throw new Error('New passwords do not match');
                }
                
                if (this.passwordForm.newPassword.length < 8) {
                    throw new Error('Password must be at least 8 characters');
                }
                
                const response = await fetch(`${API_BASE}/api/v1/account/password`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({
                        current_password: this.passwordForm.currentPassword,
                        new_password: this.passwordForm.newPassword
                    })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to change password');
                }
                
                this.showToast('Password changed successfully', 'success');
                
                // Reset form
                this.passwordForm = {
                    currentPassword: '',
                    newPassword: '',
                    confirmPassword: ''
                };
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        // ============ Faction Management (Admin) ============
        async loadFactions() {
            try {
                const response = await fetch(`${API_BASE}/api/admin/factions/list`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to load factions');
                }
                
                this.factions = data.factions || [];
                this.showToast('Factions loaded', 'success');
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        openAddFactionCredits(faction) {
            this.factionCreditsModal = faction;
            this.factionCreditsAmount = 0;
            this.factionCreditsReason = '';
        },
        
        async addFactionCredits() {
            try {
                const response = await fetch(`${API_BASE}/api/admin/factions/${this.factionCreditsModal}/add-credits`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({
                        amount: this.factionCreditsAmount,
                        reason: this.factionCreditsReason
                    })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to add credits');
                }
                
                this.showToast(`Added ¤${this.factionCreditsAmount} to ${data.users_affected} users in ${this.factionCreditsModal}`, 'success');
                this.factionCreditsModal = null;
                await this.loadFactions();
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        async createNewFaction() {
            try {
                // Validate faction name
                if (!this.newFactionName.trim()) {
                    throw new Error('Faction name is required');
                }
                
                const response = await fetch(`${API_BASE}/api/admin/factions/create`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`
                    },
                    body: JSON.stringify({
                        name: this.newFactionName.trim(),
                        description: this.newFactionDescription.trim()
                    })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to create faction');
                }
                
                this.showToast(`Faction "${this.newFactionName}" created successfully!`, 'success');
                
                // Reset form
                this.newFactionName = '';
                this.newFactionDescription = '';
                
                // Refresh faction list
                await this.loadFactions();
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        // ============ User Export (Admin) ============
        async exportUsersCSV() {
            try {
                const response = await fetch(`${API_BASE}/api/admin/users/export`, {
                    headers: { 'Authorization': `Bearer ${this.token}` }
                });
                
                if (!response.ok) {
                    throw new Error('Failed to export users');
                }
                
                // Get the blob data
                const blob = await response.blob();
                
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `users_export_${new Date().toISOString().split('T')[0]}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showToast('Export downloaded', 'success');
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },
        
        // ============ Utilities ============
        formatBalance(amount) {
            return Number(amount).toFixed(2);
        },
        
        formatTimestamp(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleString();
        },
        
        copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Copied to clipboard', 'success');
            }).catch(() => {
                this.showToast('Failed to copy', 'error');
            });
        },
        
        showToast(message, type = 'success') {
            const toast = { message, type };
            this.toasts.push(toast);
            
            setTimeout(() => {
                const index = this.toasts.indexOf(toast);
                if (index > -1) {
                    this.toasts.splice(index, 1);
                }
            }, 3000);
        }
    },
    
    watch: {
        currentView(newView) {
            if (newView === 'admin' && this.user.is_admin) {
                this.loadApiKeys();
                this.loadCasinoGames();
            }
        }
    }
}).mount('#app');
