const axios = require('axios');

const TEST_SERVER = 'http://localhost:3000/webhook';

const TEST_CASES = [
    // CASE 1: Standard Minecraft RAT format
    {
        name: "STANDARD RAT FORMAT",
        description: "Exactly what your RAT sends",
        payload: {
            content: "@everyone\nMinecraft Info for victim123",
            username: "Security Logger v3.0",
            avatar_url: "https://cdn.discordapp.com/embed/avatars/0.png",
            embeds: [
                {
                    title: "Minecraft Account",
                    description: "Session captured successfully",
                    color: 3066993,
                    fields: [
                        {
                            name: "Username",
                            value: "```\nvictim123\n```",
                            inline: true
                        },
                        {
                            name: "UUID",
                            value: "```\n550e8400-e29b-41d4-a716-446655440000\n```",
                            inline: true
                        },
                        {
                            name: "Token",
                            value: "```\neyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c\n```",
                            inline: false
                        }
                    ],
                    footer: {
                        text: "Captured at 12:34:56 UTC"
                    }
                },
                {
                    title: "Hit Summary",
                    description: "🌐 **IP:** `192.168.1.100`\n💻 **OS:** Windows 11\n🔑 **Passwords:** 42",
                    color: 15158332,
                    fields: [
                        {
                            name: "Files",
                            value: "📁 **Total:** 156\n🎮 **Minecraft:** 23\n📝 **Documents:** 42"
                        }
                    ],
                    components: [
                        {
                            type: 1,
                            components: [
                                {
                                    type: 2,
                                    label: "View Dashboard",
                                    style: 5,
                                    url: "https://ratpanel.com/dashboard"
                                },
                                {
                                    type: 2,
                                    label: "Download Logs",
                                    style: 5,
                                    url: "https://ratpanel.com/download"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    },

    // CASE 2: Code blocks with syntax highlighting
    {
        name: "CODE BLOCKS WITH SYNTAX",
        description: "Different code block types",
        payload: {
            content: "@here Check this code",
            embeds: [
                {
                    title: "Code Samples",
                    description: "Various syntax highlighting",
                    color: 3447003,
                    fields: [
                        {
                            name: "JSON",
                            value: "```json\n{\n  \"username\": \"player1\",\n  \"premium\": true,\n  \"coins\": 15000\n}\n```"
                        },
                        {
                            name: "Java",
                            value: "```java\npublic class MinecraftMod {\n    public static void main(String[] args) {\n        System.out.println(\"RAT active\");\n    }\n}\n```"
                        },
                        {
                            name: "Fix block",
                            value: "```fix\nCRITICAL: Session valid for 2 hours\n```"
                        },
                        {
                            name: "Diff block",
                            value: "```diff\n+ Added: 15 passwords\n- Removed: 2 files\n```"
                        }
                    ]
                },
                {
                    title: "SKIP THIS EMBED",
                    description: "Should not appear in his channel",
                    color: 0xff0000
                }
            ]
        }
    },

    // CASE 3: Inline fields with mixed content
    {
        name: "MIXED INLINE FIELDS",
        description: "Complex inline field arrangement",
        payload: {
            content: "<@&1234567890> Alert!",
            embeds: [
                {
                    title: "Player Statistics",
                    color: 0x9b59b6,
                    fields: [
                        { name: "Kills", value: "1,234", inline: true },
                        { name: "Deaths", value: "567", inline: true },
                        { name: "K/D", value: "2.17", inline: true },
                        { name: "Playtime", value: "342h 12m", inline: true },
                        { name: "Rank", value: "Admin", inline: true },
                        { name: "Server", value: "hypixel.net", inline: true },
                        { name: "Achievements", value: "```\n• Speedrunner\n• Collector\n• Builder\n```", inline: false }
                    ]
                }
            ]
        }
    },

    // CASE 4: No @everyone, just embeds
    {
        name: "NO @EVERYONE",
        description: "Only embeds, no mention",
        payload: {
            username: "Silent Logger",
            embeds: [
                {
                    title: "Silent Capture",
                    description: "No @everyone in this message",
                    color: 0x3498db,
                    fields: [
                        { name: "Status", value: "✅ Stealth mode" },
                        { name: "Files", value: "📁 8 captured" }
                    ]
                }
            ]
        }
    },

    // CASE 5: Just @everyone, minimal embed
    {
        name: "MINIMAL EMBED",
        description: "@everyone with basic embed",
        payload: {
            content: "@everyone",
            embeds: [
                {
                    description: "Simple notification",
                    color: 0xffff00
                }
            ]
        }
    },

    // CASE 6: Multiple embeds (4 total)
    {
        name: "MULTIPLE EMBEDS",
        description: "4 embeds, should only forward first",
        payload: {
            content: "Testing multiple embeds",
            embeds: [
                { title: "EMBED 1 (FORWARD)", description: "This should forward", color: 0x00ff00 },
                { title: "EMBED 2 (SKIP)", description: "This should NOT forward", color: 0xff0000 },
                { title: "EMBED 3 (SKIP)", description: "This should NOT forward", color: 0x0000ff },
                { title: "EMBED 4 (SKIP)", description: "This should NOT forward", color: 0xff00ff }
            ]
        }
    },

    // CASE 7: Empty embed with only color
    {
        name: "EMPTY EMBED",
        description: "Embed with only color field",
        payload: {
            content: "@everyone Color test",
            embeds: [
                {
                    color: 0xff9900
                }
            ]
        }
    },

    // CASE 8: Embed with image/thumbnail
    {
        name: "EMBED WITH MEDIA",
        description: "Includes thumbnail and image",
        payload: {
            content: "@everyone Media test",
            embeds: [
                {
                    title: "Player Skin",
                    description: "Victim's Minecraft skin",
                    color: 0x1abc9c,
                    thumbnail: {
                        url: "https://mc-heads.net/avatar/victim123"
                    },
                    image: {
                        url: "https://mc-heads.net/body/victim123"
                    }
                }
            ]
        }
    },

    // CASE 9: Embed with author and footer
    {
        name: "EMBED WITH AUTHOR/FOOTER",
        description: "Full embed structure",
        payload: {
            embeds: [
                {
                    author: {
                        name: "RAT Logger Pro",
                        icon_url: "https://cdn.discordapp.com/embed/avatars/1.png"
                    },
                    title: "Full Featured Embed",
                    description: "This embed has everything",
                    color: 0xe74c3c,
                    fields: [
                        { name: "Field 1", value: "Value 1", inline: true },
                        { name: "Field 2", value: "Value 2", inline: true }
                    ],
                    footer: {
                        text: "Logged at 12:34:56 UTC",
                        icon_url: "https://cdn.discordapp.com/embed/avatars/2.png"
                    }
                }
            ]
        }
    },

    // CASE 10: Special Discord formatting
    {
        name: "SPECIAL FORMATTING",
        description: "Markdown, spoilers, etc.",
        payload: {
            content: "@everyone **Bold** *Italic* __Underline__ ~~Strike~~",
            embeds: [
                {
                    title: "Formatting Test",
                    description: "**Bold text**\n*Italic text*\n__Underline__\n~~Strikethrough~~\n||spoiler||\n`inline code`\n```\ncode block\n```\n[Link](https://discord.com)",
                    color: 0x7289da,
                    fields: [
                        { name: "**Bold Field**", value: "*Italic value*", inline: true },
                        { name: "__Underline__", value: "~~Strike~~", inline: true }
                    ]
                }
            ]
        }
    },

    // CASE 11: Very long content
    {
        name: "LONG CONTENT",
        description: "Tests content/field length limits",
        payload: {
            content: "@everyone " + "A".repeat(100),
            embeds: [
                {
                    title: "L".repeat(50),
                    description: "D".repeat(1000),
                    color: 0xf1c40f,
                    fields: Array.from({length: 10}, (_, i) => ({
                        name: `Field ${i}`.repeat(10),
                        value: `Value ${i}`.repeat(50),
                        inline: i % 3 !== 0
                    }))
                },
                {
                    title: "Second Embed",
                    description: "Should not appear"
                }
            ]
        }
    },

    // CASE 12: Empty/missing fields
    {
        name: "EDGE CASES",
        description: "Null, undefined, empty values",
        payload: {
            content: null,
            username: undefined,
            embeds: [
                {
                    title: "",
                    description: null,
                    fields: [],
                    color: 0
                }
            ]
        }
    }
];

async function runTest(testCase, index) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`TEST ${index + 1}/${TEST_CASES.length}: ${testCase.name}`);
    console.log(`${'='.repeat(60)}`);
    console.log(`Description: ${testCase.description}`);
    
    try {
        // Clean payload (remove undefined values)
        const cleanPayload = JSON.parse(JSON.stringify(testCase.payload));
        
        console.log('\n📤 Sending payload:');
        console.log(JSON.stringify(cleanPayload, null, 2).substring(0, 500) + '...');
        
        const response = await axios.post(TEST_SERVER, cleanPayload, {
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json',
                'X-Test-Case': testCase.name
            }
        });
        
        console.log('\n✅ Server response:', response.data);
        console.log(`\n📊 Expected result:`);
        console.log(`- YOUR webhook: Should receive ALL ${cleanPayload.embeds?.length || 0} embeds`);
        console.log(`- HIS webhook: Should receive ONLY:`);
        console.log(`  • Content: "${cleanPayload.content?.substring(0, 50) || '(none)'}..."`);
        console.log(`  • First embed: "${cleanPayload.embeds?.[0]?.title || 'No title'}"`);
        console.log(`  • Total embeds: 1 (only first)`);
        
        if (cleanPayload.embeds?.[0]?.components?.length > 0) {
            console.log(`  • Components removed: ${cleanPayload.embeds[0].components.length} buttons`);
        }
        
        return { success: true, test: testCase.name };
        
    } catch (error) {
        console.log(`\n❌ Test FAILED: ${error.message}`);
        if (error.response) {
            console.log('Response status:', error.response.status);
            console.log('Response data:', error.response.data);
        }
        return { success: false, test: testCase.name, error: error.message };
    }
}

async function runAllTests() {
    console.log(`
╔══════════════════════════════════════════════════════════╗
║                  WEBHOOK RELAY TEST SUITE                ║
║                  COMPREHENSIVE FORMAT TESTS              ║
╚══════════════════════════════════════════════════════════╝
    
📡 Target Server: ${TEST_SERVER}
📊 Total Tests: ${TEST_CASES.length}
⏱️  Starting tests...
    `);
    
    const results = {
        passed: 0,
        failed: 0,
        details: []
    };
    
    // Run tests one by one with delay
    for (let i = 0; i < TEST_CASES.length; i++) {
        const result = await runTest(TEST_CASES[i], i);
        results.details.push(result);
        
        if (result.success) {
            results.passed++;
            console.log('✅ TEST PASSED');
        } else {
            results.failed++;
            console.log('❌ TEST FAILED');
        }
        
        // Wait 2 seconds between tests to avoid rate limits
        if (i < TEST_CASES.length - 1) {
            console.log('\n⏳ Waiting 2 seconds before next test...');
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
    
    // Summary
    console.log(`\n${'='.repeat(60)}`);
    console.log('📋 TEST SUMMARY');
    console.log(`${'='.repeat(60)}`);
    console.log(`✅ Passed: ${results.passed}/${TEST_CASES.length}`);
    console.log(`❌ Failed: ${results.failed}/${TEST_CASES.length}`);
    console.log(`📈 Success Rate: ${((results.passed / TEST_CASES.length) * 100).toFixed(1)}%`);
    
    console.log('\n🔍 Failed tests:');
    results.details.filter(r => !r.success).forEach(r => {
        console.log(`   • ${r.test}: ${r.error}`);
    });
    
    console.log('\n📝 Test coverage:');
    console.log('   1. Standard RAT format ✓');
    console.log('   2. Code blocks with syntax ✓');
    console.log('   3. Inline field layouts ✓');
    console.log('   4. No @everyone case ✓');
    console.log('   5. Minimal embed ✓');
    console.log('   6. Multiple embeds (4) ✓');
    console.log('   7. Empty embed ✓');
    console.log('   8. Embed with media ✓');
    console.log('   9. Author/footer ✓');
    console.log('   10. Special formatting ✓');
    console.log('   11. Length limits ✓');
    console.log('   12. Edge cases ✓');
    
    console.log(`\n🎯 Verification Checklist:`);
    console.log(`   • Check YOUR Discord: Should have ${TEST_CASES.length} messages`);
    console.log(`   • Check HIS Discord: Should have ${TEST_CASES.length} messages`);
    console.log(`   • Each of HIS messages should have ONLY 1 embed`);
    console.log(`   • HIS messages should NEVER have 2nd embed or buttons`);
    console.log(`   • All formatting should be preserved (code blocks, colors, etc.)`);
}

// Run tests
runAllTests().catch(console.error);
