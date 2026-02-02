require('dotenv').config();
const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

const BOT_TOKEN = process.env.BOT_TOKEN;
const HIS_WEBHOOK = process.env.HIS_WEBHOOK;
const YOUR_CHANNEL_ID = process.env.YOUR_CHANNEL_ID;

if (!BOT_TOKEN || !HIS_WEBHOOK || !YOUR_CHANNEL_ID) {
    console.error('❌ ERROR: Set BOT_TOKEN, HIS_WEBHOOK, YOUR_CHANNEL_ID in .env file!');
    process.exit(1);
}

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

console.log('🤖 Discord Forwarder Bot Starting...');

client.on('ready', () => {
    console.log(`✅ Bot logged in as: ${client.user.tag}`);
    
    const channel = client.channels.cache.get(YOUR_CHANNEL_ID);
    if (channel) {
        console.log(`📺 Monitoring: #${channel.name} in ${channel.guild.name}`);
    } else {
        console.log(`❌ Channel ${YOUR_CHANNEL_ID} not found!`);
    }
});

client.on('messageCreate', async (message) => {
    // Only your channel
    if (message.channelId !== YOUR_CHANNEL_ID) return;
    
    // Skip bot messages
    if (message.author.bot) return;
    
    // Check if has @everyone AND embeds
    if (message.content.includes('@everyone') && message.embeds.length > 0) {
        console.log(`📨 Forwarding: ${message.content.substring(0, 50)}...`);
        
        // Get first embed
        const firstEmbed = message.embeds[0].data;
        
        // Create payload
        const payload = {
            content: message.content,
            username: message.author.username,
            avatar_url: message.author.displayAvatarURL({ extension: 'png', size: 256 }),
            embeds: [firstEmbed]
        };
        
        // Remove buttons if exists
        if (payload.embeds[0].components) {
            delete payload.embeds[0].components;
        }
        
        // Send to his webhook
        try {
            await axios.post(HIS_WEBHOOK, payload);
            console.log('✅ Forwarded to his webhook!');
        } catch (error) {
            console.log('❌ Forward failed:', error.message);
        }
    }
});

// Login
client.login(BOT_TOKEN).catch(error => {
    console.log('❌ Login failed:', error);
});
