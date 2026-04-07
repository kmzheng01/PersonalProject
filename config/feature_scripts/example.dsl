# AudioStream - Example DSL Feature Script

# Auto Next Track when current finishes
define FEATURE "AutoNext" {
    on_song_end {
        next()
        display_show("Next: {now_playing}")
    }
}

# Keyboard shortcuts simulation
define FEATURE "Shortcuts" {
    on_key_press "space" {
        toggle_play()
    }
    
    on_key_press "right" {
        next()
    }
    
    on_key_press "left" {
        previous()
    }
}

# Volume fade on song transition
define FEATURE "VolumeFade" {
    on_song_end {
        # Fade out current
        set_volume(0.8)
        sleep(100)
        set_volume(0.6)
        sleep(100)
        set_volume(0.4)
        sleep(100)
        set_volume(0.2)
        sleep(100)
        set_volume(0.0)
        
        # Play next
        next()
        
        # Fade in new
        set_volume(0.0)
        sleep(100)
        set_volume(0.2)
        sleep(100)
        set_volume(0.4)
        sleep(100)
        set_volume(0.6)
        sleep(100)
        set_volume(0.8)
    }
}

# Display now playing info
define FEATURE "DisplayInfo" {
    on_play {
        now_info = now_playing()
        display_show(now_info.title)
    }
    
    on_stop {
        display_clear()
    }
}
