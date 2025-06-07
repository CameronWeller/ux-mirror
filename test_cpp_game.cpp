#define OLC_PGE_APPLICATION
#include "pixel_game_engine/olcPixelGameEngine.h"

#include <vector>
#include <string>
#include <random>

// Simple C++ Game for UX Testing
// Features: Menu system, HUD, buttons, score display, settings
class UXTestGame : public olc::PixelGameEngine
{
public:
    UXTestGame()
    {
        sAppName = "UX Test Game - C++ Edition";
    }

private:
    enum GameState {
        MENU,
        PLAYING,
        SETTINGS,
        GAME_OVER
    };

    GameState currentState = MENU;
    
    // Game variables
    float playerX = 50.0f, playerY = 50.0f;
    float playerSpeed = 100.0f;
    int score = 0;
    int lives = 3;
    float gameTime = 0.0f;
    
    // Menu variables
    int selectedMenuItem = 0;
    std::vector<std::string> menuItems = {"Start Game", "Settings", "Exit"};
    
    // Settings variables
    int volume = 50;
    bool fullscreen = false;
    int difficulty = 1; // 0=Easy, 1=Medium, 2=Hard
    
    // Enemies
    struct Enemy {
        float x, y;
        float dx, dy;
        int health;
        olc::Pixel color;
    };
    std::vector<Enemy> enemies;
    
    // UI Button structure
    struct Button {
        float x, y, w, h;
        std::string text;
        olc::Pixel color;
        bool enabled;
        
        bool IsClicked(float mouseX, float mouseY) {
            return mouseX >= x && mouseX <= x + w && 
                   mouseY >= y && mouseY <= y + h && enabled;
        }
    };
    
    std::vector<Button> menuButtons;
    std::vector<Button> settingsButtons;
    
    // Random engine
    std::random_device rd;
    std::mt19937 gen{rd()};

public:
    bool OnUserCreate() override
    {
        // Initialize menu buttons
        menuButtons.clear();
        menuButtons.push_back({50, 100, 150, 40, "Start Game", olc::GREEN, true});
        menuButtons.push_back({50, 160, 150, 40, "Settings", olc::BLUE, true});
        menuButtons.push_back({50, 220, 150, 40, "Exit", olc::RED, true});
        
        // Initialize settings buttons
        settingsButtons.clear();
        settingsButtons.push_back({50, 100, 100, 30, "Volume -", olc::YELLOW, true});
        settingsButtons.push_back({160, 100, 100, 30, "Volume +", olc::YELLOW, true});
        settingsButtons.push_back({50, 150, 200, 30, "Toggle Fullscreen", olc::CYAN, true});
        settingsButtons.push_back({50, 200, 100, 30, "Easy", olc::GREEN, true});
        settingsButtons.push_back({160, 200, 100, 30, "Medium", olc::YELLOW, true});
        settingsButtons.push_back({270, 200, 100, 30, "Hard", olc::RED, true});
        settingsButtons.push_back({50, 280, 100, 30, "Back", olc::WHITE, true});
        
        return true;
    }

    bool OnUserUpdate(float fElapsedTime) override
    {
        gameTime += fElapsedTime;
        
        switch (currentState) {
            case MENU:
                UpdateMenu(fElapsedTime);
                break;
            case PLAYING:
                UpdateGame(fElapsedTime);
                break;
            case SETTINGS:
                UpdateSettings(fElapsedTime);
                break;
            case GAME_OVER:
                UpdateGameOver(fElapsedTime);
                break;
        }
        
        return true;
    }
    
private:
    void UpdateMenu(float fElapsedTime) {
        Clear(olc::BLACK);
        
        // Draw title
        DrawString(50, 30, "UX TEST GAME", olc::WHITE, 2);
        DrawString(50, 50, "C++ Edition with UI Elements", olc::GREY, 1);
        
        // Handle input
        if (GetKey(olc::Key::UP).bPressed && selectedMenuItem > 0) selectedMenuItem--;
        if (GetKey(olc::Key::DOWN).bPressed && selectedMenuItem < menuItems.size() - 1) selectedMenuItem++;
        if (GetKey(olc::Key::ENTER).bPressed) {
            switch (selectedMenuItem) {
                case 0: // Start Game
                    currentState = PLAYING;
                    InitializeGame();
                    break;
                case 1: // Settings
                    currentState = SETTINGS;
                    break;
                case 2: // Exit
                    return;
            }
        }
        
        // Draw menu buttons with visual feedback
        for (int i = 0; i < menuButtons.size(); i++) {
            auto& btn = menuButtons[i];
            olc::Pixel buttonColor = btn.color;
            if (i == selectedMenuItem) {
                buttonColor = olc::WHITE;
                // Draw selection highlight
                FillRect(btn.x - 5, btn.y - 5, btn.w + 10, btn.h + 10, olc::DARK_YELLOW);
            }
            
            FillRect(btn.x, btn.y, btn.w, btn.h, buttonColor);
            DrawRect(btn.x, btn.y, btn.w, btn.h, olc::WHITE);
            DrawString(btn.x + 10, btn.y + 15, btn.text, olc::BLACK);
        }
        
        // Mouse interaction
        olc::vi2d mousePos = GetMousePos();
        if (GetMouse(0).bPressed) {
            for (int i = 0; i < menuButtons.size(); i++) {
                if (menuButtons[i].IsClicked(mousePos.x, mousePos.y)) {
                    selectedMenuItem = i;
                    // Trigger same action as ENTER key
                    switch (i) {
                        case 0: currentState = PLAYING; InitializeGame(); break;
                        case 1: currentState = SETTINGS; break;
                        case 2: return;
                    }
                }
            }
        }
        
        // Instructions
        DrawString(300, 100, "Controls:", olc::GREEN);
        DrawString(300, 120, "Arrow Keys: Navigate", olc::WHITE);
        DrawString(300, 140, "Enter: Select", olc::WHITE);
        DrawString(300, 160, "Mouse: Click buttons", olc::WHITE);
        DrawString(300, 200, "Game Features:", olc::GREEN);
        DrawString(300, 220, "- Menu system", olc::WHITE);
        DrawString(300, 240, "- Settings panel", olc::WHITE);
        DrawString(300, 260, "- HUD elements", olc::WHITE);
        DrawString(300, 280, "- Button interactions", olc::WHITE);
    }
    
    void UpdateGame(float fElapsedTime) {
        Clear(olc::DARK_BLUE);
        
        // Player movement
        if (GetKey(olc::Key::A).bHeld || GetKey(olc::Key::LEFT).bHeld) playerX -= playerSpeed * fElapsedTime;
        if (GetKey(olc::Key::D).bHeld || GetKey(olc::Key::RIGHT).bHeld) playerX += playerSpeed * fElapsedTime;
        if (GetKey(olc::Key::W).bHeld || GetKey(olc::Key::UP).bHeld) playerY -= playerSpeed * fElapsedTime;
        if (GetKey(olc::Key::S).bHeld || GetKey(olc::Key::DOWN).bHeld) playerY += playerSpeed * fElapsedTime;
        
        // Keep player in bounds
        playerX = std::max(10.0f, std::min(playerX, float(ScreenWidth() - 20)));
        playerY = std::max(50.0f, std::min(playerY, float(ScreenHeight() - 20)));
        
        // Spawn enemies
        if (fmod(gameTime, 2.0f) < fElapsedTime) {
            std::uniform_real_distribution<float> dis(50, ScreenWidth() - 50);
            enemies.push_back({dis(gen), 10, 0, 50 + difficulty * 30, 3, olc::RED});
        }
        
        // Update enemies
        for (auto& enemy : enemies) {
            enemy.y += enemy.dy * fElapsedTime;
        }
        
        // Remove off-screen enemies and update score
        enemies.erase(std::remove_if(enemies.begin(), enemies.end(), 
            [this](const Enemy& e) { 
                if (e.y > ScreenHeight()) {
                    score += 10;
                    return true;
                }
                return false;
            }), enemies.end());
        
        // Check collisions
        for (auto it = enemies.begin(); it != enemies.end();) {
            float dx = it->x - playerX;
            float dy = it->y - playerY;
            if (sqrt(dx*dx + dy*dy) < 20) {
                lives--;
                it = enemies.erase(it);
                if (lives <= 0) {
                    currentState = GAME_OVER;
                    return;
                }
            } else {
                ++it;
            }
        }
        
        // Draw player
        FillCircle(playerX, playerY, 8, olc::GREEN);
        DrawCircle(playerX, playerY, 8, olc::WHITE);
        
        // Draw enemies
        for (const auto& enemy : enemies) {
            FillCircle(enemy.x, enemy.y, 6, enemy.color);
            DrawCircle(enemy.x, enemy.y, 6, olc::WHITE);
        }
        
        // Draw HUD (this is what we want to analyze and improve)
        DrawHUD();
        
        // Pause/Menu
        if (GetKey(olc::Key::ESCAPE).bPressed) {
            currentState = MENU;
        }
    }
    
    void UpdateSettings(float fElapsedTime) {
        Clear(olc::DARK_GREY);
        
        // Title
        DrawString(50, 30, "SETTINGS", olc::WHITE, 2);
        
        // Volume setting
        DrawString(50, 80, "Volume: " + std::to_string(volume) + "%", olc::WHITE);
        
        // Fullscreen setting
        DrawString(50, 130, "Fullscreen: " + std::string(fullscreen ? "ON" : "OFF"), olc::WHITE);
        
        // Difficulty setting
        DrawString(50, 180, "Difficulty:", olc::WHITE);
        
        // Draw settings buttons
        for (int i = 0; i < settingsButtons.size(); i++) {
            auto& btn = settingsButtons[i];
            olc::Pixel color = btn.color;
            
            // Highlight active difficulty
            if (i >= 3 && i <= 5 && (i - 3) == difficulty) {
                color = olc::WHITE;
            }
            
            FillRect(btn.x, btn.y, btn.w, btn.h, color);
            DrawRect(btn.x, btn.y, btn.w, btn.h, olc::BLACK);
            DrawString(btn.x + 5, btn.y + 10, btn.text, olc::BLACK);
        }
        
        // Mouse interaction
        olc::vi2d mousePos = GetMousePos();
        if (GetMouse(0).bPressed) {
            for (int i = 0; i < settingsButtons.size(); i++) {
                if (settingsButtons[i].IsClicked(mousePos.x, mousePos.y)) {
                    switch (i) {
                        case 0: volume = std::max(0, volume - 10); break;
                        case 1: volume = std::min(100, volume + 10); break;
                        case 2: fullscreen = !fullscreen; break;
                        case 3: difficulty = 0; break;
                        case 4: difficulty = 1; break;
                        case 5: difficulty = 2; break;
                        case 6: currentState = MENU; break;
                    }
                }
            }
        }
        
        if (GetKey(olc::Key::ESCAPE).bPressed) {
            currentState = MENU;
        }
    }
    
    void UpdateGameOver(float fElapsedTime) {
        Clear(olc::DARK_RED);
        
        DrawString(100, 100, "GAME OVER", olc::WHITE, 3);
        DrawString(100, 150, "Final Score: " + std::to_string(score), olc::YELLOW, 2);
        DrawString(100, 200, "Press ENTER to return to menu", olc::WHITE);
        DrawString(100, 220, "Press SPACE to play again", olc::WHITE);
        
        if (GetKey(olc::Key::ENTER).bPressed) {
            currentState = MENU;
        }
        if (GetKey(olc::Key::SPACE).bPressed) {
            currentState = PLAYING;
            InitializeGame();
        }
    }
    
    void DrawHUD() {
        // HUD Background
        FillRect(0, 0, ScreenWidth(), 40, olc::DARK_GREY);
        DrawLine(0, 40, ScreenWidth(), 40, olc::WHITE);
        
        // Score
        DrawString(10, 10, "Score: " + std::to_string(score), olc::YELLOW);
        
        // Lives with visual representation
        DrawString(150, 10, "Lives: ", olc::WHITE);
        for (int i = 0; i < lives; i++) {
            FillCircle(200 + i * 20, 20, 5, olc::GREEN);
        }
        
        // Time
        DrawString(300, 10, "Time: " + std::to_string(int(gameTime)), olc::CYAN);
        
        // Mini-map area (example UI element)
        DrawRect(ScreenWidth() - 120, 10, 100, 80, olc::WHITE);
        DrawString(ScreenWidth() - 115, 15, "Mini-Map", olc::WHITE);
        FillCircle(ScreenWidth() - 70, 50, 2, olc::GREEN); // Player dot
        
        // Health bar example
        DrawString(10, ScreenHeight() - 30, "Health:", olc::WHITE);
        DrawRect(60, ScreenHeight() - 25, 100, 10, olc::WHITE);
        FillRect(61, ScreenHeight() - 24, lives * 33, 8, olc::GREEN);
        
        // Action buttons overlay
        DrawString(ScreenWidth() - 200, ScreenHeight() - 30, "ESC: Menu", olc::GREY);
    }
    
    void InitializeGame() {
        playerX = 50.0f;
        playerY = 100.0f;
        score = 0;
        lives = 3;
        gameTime = 0.0f;
        enemies.clear();
    }
};

int main()
{
    UXTestGame game;
    if (game.Construct(640, 480, 2, 2))
        game.Start();
    return 0;
} 