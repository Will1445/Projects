#include <iostream>
#include <thread>
#include <cstring>
#include <vector>
#include <algorithm>
#include <cctype>
#include <map>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/extensions/XTest.h>

#define PORT_CMD 5000
#define PORT_STREAM 5001
#define PORT_MOUSE 5003
#define SCREEN_WIDTH 1440
#define SCREEN_HEIGHT 900

// Debug logging
#define LOG(msg) std::cout << "[+] " << msg << std::endl
#define ERR(msg) std::cerr << "[-] ERROR: " << msg << std::endl

static std::string translate_key_name(const std::string& key) {
    static const std::map<std::string, std::string> keymap = {
        {"ctrl", "Control_L"}, {"control", "Control_L"},
        {"alt", "Alt_L"}, {"altgr", "Alt_R"},
        {"shift", "Shift_L"}, {"enter", "Return"},
        {"esc", "Escape"}, {"f1", "F1"}, {"f2", "F2"}, {"f3", "F3"},
        {"f4", "F4"}, {"f5", "F5"}, {"f6", "F6"}, {"f7", "F7"},
        {"f8", "F8"}, {"f9", "F9"}, {"f10", "F10"}, {"f11", "F11"},
        {"f12", "F12"}, {"super", "Super_L"}, {"win", "Super_L"},
        {"space", "space"}, {"tab", "Tab"}, {"backspace", "BackSpace"}
    };

    std::string lower_key;
    std::transform(key.begin(), key.end(), std::back_inserter(lower_key), ::tolower);
    
    auto it = keymap.find(lower_key);
    return (it != keymap.end()) ? it->second : key;
}

int create_server(int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(sock, (sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(sock);
        exit(EXIT_FAILURE);
    }

    if (listen(sock, 1) < 0) {
        perror("listen");
        close(sock);
        exit(EXIT_FAILURE);
    }

    LOG("Server started on port " << port);
    return sock;
}


static bool send_all(int sock, const char* data, size_t len) {
    size_t total = 0;
    while (total < len) {
        ssize_t sent = send(sock, data + total, len - total, 0);
        if (sent <= 0) return false;
        total += static_cast<size_t>(sent);
    }
    return true;
}

void type_text(Display* display, const std::string& text) {
    for (char c : text) {
        if (c == ' ') {
            KeyCode space_code = XKeysymToKeycode(display, XK_space);
            XTestFakeKeyEvent(display, space_code, True, CurrentTime);
            XTestFakeKeyEvent(display, space_code, False, CurrentTime);
            XFlush(display);
            usleep(10000);
            continue;
        }

        bool needs_shift = std::isupper(static_cast<unsigned char>(c));
        char lower_c = std::tolower(static_cast<unsigned char>(c));
        
        KeySym keysym = XStringToKeysym(std::string(1, lower_c).c_str());
        KeyCode keycode = XKeysymToKeycode(display, keysym);
        KeyCode shift_code = XKeysymToKeycode(display, XK_Shift_L);

        if (keycode == 0) continue;

        if (needs_shift) {
            XTestFakeKeyEvent(display, shift_code, True, CurrentTime);
        }

        XTestFakeKeyEvent(display, keycode, True, CurrentTime);
        XTestFakeKeyEvent(display, keycode, False, CurrentTime);

        if (needs_shift) {
            XTestFakeKeyEvent(display, shift_code, False, CurrentTime);
        }

        XFlush(display);
        usleep(10000);
    }
}

void handle_key_sequence(Display* display, const std::string& sequence) {
    std::vector<std::string> keys;
    size_t pos = 0;
    std::string s = sequence;

    while ((pos = s.find('+')) != std::string::npos) {
        keys.push_back(translate_key_name(s.substr(0, pos)));
        s.erase(0, pos + 1);
    }
    keys.push_back(translate_key_name(s));

    std::vector<KeyCode> keycodes;
    for (const auto& key : keys) {
        KeySym keysym = XStringToKeysym(key.c_str());
        if (keysym == NoSymbol) continue;

        KeyCode code = XKeysymToKeycode(display, keysym);
        if (code == 0) continue;
        keycodes.push_back(code);
    }

    for (auto code : keycodes) {
        XTestFakeKeyEvent(display, code, True, CurrentTime);
    }
    XFlush(display);
    usleep(10000);

    for (auto it = keycodes.rbegin(); it != keycodes.rend(); ++it) {
        XTestFakeKeyEvent(display, *it, False, CurrentTime);
    }
    XFlush(display);
}


static void trim_trailing_newlines(std::string& s) {
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r' || s.back() == '\0')) s.pop_back();
}

void handle_command(int client_sock) {
    Display* display = XOpenDisplay(nullptr);
    if (!display) {
        ERR("Failed to open X display");
        close(client_sock);
        return;
    }

    char buffer[1024];
    std::string recvbuf;
    try {
        while (true) {
            ssize_t r = recv(client_sock, buffer, sizeof(buffer), 0);
            if (r <= 0) break;

            recvbuf.append(buffer, static_cast<size_t>(r));


            std::string cmd = recvbuf;
            trim_trailing_newlines(cmd);
            recvbuf.clear();

            if (cmd.empty()) continue;

            if (cmd.rfind("cmd:", 0) == 0) {
                std::string command = cmd.substr(4);
                LOG("Executing: " << command);


                FILE* pipe = popen(command.c_str(), "r");
                if (!pipe) {
                    std::string err = "Failed to execute command\n<<END>>";
                    send_all(client_sock, err.c_str(), err.size());
                    continue;
                }

                std::string output;
                char outbuf[4096];
                while (fgets(outbuf, sizeof(outbuf), pipe) != nullptr) {
                    output.append(outbuf);
                }
                int status = pclose(pipe);


                if (output.empty()) output = "\n"; 

                // Send full output and an END marker
                if (!send_all(client_sock, output.c_str(), output.size())) break;
                const char end_marker[] = "<<END>>";
                if (!send_all(client_sock, end_marker, sizeof(end_marker) - 1)) break;

                (void)status;
            }
            else if (cmd.rfind("key:", 0) == 0) {
                std::string key_seq = cmd.substr(4);
                LOG("Sending keys: " << key_seq);
                handle_key_sequence(display, key_seq);
            }
            else {
                LOG("Typing text: " << cmd);
                type_text(display, cmd);
            }
        }
    } catch (...) {}

    XCloseDisplay(display);
    close(client_sock);
}

void screen_stream(int client_sock) {
    Display* display = XOpenDisplay(nullptr);
    if (!display) {
        ERR("Failed to open X display");
        close(client_sock);
        return;
    }

    Window root = DefaultRootWindow(display);
    uint32_t dims[2] = {htonl(SCREEN_WIDTH), htonl(SCREEN_HEIGHT)};
    send(client_sock, dims, sizeof(dims), 0);

    try {
        while (true) {
            XImage* img = XGetImage(display, root, 0, 0, 
                                  SCREEN_WIDTH, SCREEN_HEIGHT, 
                                  AllPlanes, ZPixmap);
            if (!img) break;

            send(client_sock, img->data, SCREEN_WIDTH * SCREEN_HEIGHT * 4, 0);
            XDestroyImage(img);
            usleep(50000);
        }
    } catch (...) {}

    XCloseDisplay(display);
    close(client_sock);
}

void handle_mouse(int client_sock) {
    Display* display = XOpenDisplay(nullptr);
    if (!display) {
        ERR("Failed to open X display");
        close(client_sock);
        return;
    }

    char buffer[64];
    try {
        while (recv(client_sock, buffer, sizeof(buffer), 0) > 0) {
            float x, y;
            if (sscanf(buffer, "move %f %f", &x, &y) == 2) {
                XWarpPointer(display, None, None, 0, 0, 0, 0, 
                            static_cast<int>(x * SCREEN_WIDTH), static_cast<int>(y * SCREEN_HEIGHT));
            }
            else if (strstr(buffer, "click")) {
                int button = (strstr(buffer, "1")) ? 1 : 2;
                if (strstr(buffer, "down")) {
                    XTestFakeButtonEvent(display, button, True, CurrentTime);
                } else {
                    XTestFakeButtonEvent(display, button, False, CurrentTime);
                }
            }
            XFlush(display);
        }
    } catch (...) {}

    XCloseDisplay(display);
    close(client_sock);
}

int main() {
    LOG("Starting server...");
    
    int cmd_sock = create_server(PORT_CMD);
    int stream_sock = create_server(PORT_STREAM);
    int mouse_sock = create_server(PORT_MOUSE);

    while (true) {
        sockaddr_in client_addr{};
        socklen_t addr_len = sizeof(client_addr);
        
        int cmd_client = accept(cmd_sock, (sockaddr*)&client_addr, &addr_len);
        if (cmd_client > 0) {
            std::thread(handle_command, cmd_client).detach();
        }

        int stream_client = accept(stream_sock, (sockaddr*)&client_addr, &addr_len);
        if (stream_client > 0) {
            std::thread(screen_stream, stream_client).detach();
        }

        int mouse_client = accept(mouse_sock, (sockaddr*)&client_addr, &addr_len);
        if (mouse_client > 0) {
            std::thread(handle_mouse, mouse_client).detach();
        }
    }

    close(cmd_sock);
    close(stream_sock);
    close(mouse_sock);
    return 0;
}