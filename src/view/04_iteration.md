# การวนซ้ำ

ไม่ว่าคุณจะแสดงรายการสิ่งที่ต้องทำ ตาราง หรือรูปภาพสินค้า การวนซ้ำบนรายการไอเท็มถือเป็นงานที่พบบ่อยในเว็บแอปพลิเคชัน การปรับความแตกต่างระหว่างชุดไอเท็มที่เปลี่ยนแปลงไปก็เป็นหนึ่งในงานที่ยากที่สุดสำหรับเฟรมเวิร์กที่จะจัดการได้ดีเช่นกัน

Leptos รองรับรูปแบบที่แตกต่างกันสองแบบสำหรับการวนซ้ำบนไอเท็ม:

1. สำหรับวิวแบบสแตติก: `Vec<_>`
2. สำหรับรายการแบบไดนามิก: `<For/>`

## วิวแบบสแตติกด้วย `Vec<_>`

บางครั้งคุณจำเป็นต้องแสดงไอเท็มซ้ำๆ แต่รายการต้นทางที่คุณดึงข้อมูลมาไม่ค่อยเปลี่ยนแปลง ในกรณีนี้ สิ่งสำคัญคือต้องรู้ว่าคุณสามารถแทรก `Vec<IV> where IV: IntoView` ใดก็ได้ลงในวิวของคุณ พูดอีกอย่างคือ ถ้าคุณเรนเดอร์ `T` ได้ คุณก็เรนเดอร์ `Vec<T>` ได้เช่นกัน

```rust
let values = vec![0, 1, 2];
view! {
    // this will just render "012"
    <p>{values.clone()}</p>
    // or we can wrap them in <li>
    <ul>
        {values.into_iter()
            .map(|n| view! { <li>{n}</li>})
            .collect::<Vec<_>>()}
    </ul>
}
```

Leptos ยังมีฟังก์ชันตัวช่วย `.collect_view()` ที่ให้คุณรวบรวมอิเทอเรเตอร์ใดๆ ของ `T: IntoView` ให้กลายเป็น `Vec<View>` ได้

```rust
let values = vec![0, 1, 2];
view! {
    // this will just render "012"
    <p>{values.clone()}</p>
    // or we can wrap them in <li>
    <ul>
        {values.into_iter()
            .map(|n| view! { <li>{n}</li>})
            .collect_view()}
    </ul>
}
```

การที่ *รายการ* เป็นแบบสแตติกไม่ได้หมายความว่าอินเทอร์เฟซต้องเป็นแบบสแตติกด้วย คุณสามารถเรนเดอร์ไอเท็มแบบไดนามิกให้เป็นส่วนหนึ่งของรายการแบบสแตติกได้

```rust
// create a list of 5 signals
let length = 5;
let counters = (1..=length).map(|idx| RwSignal::new(idx));
```

สังเกตว่าตรงนี้แทนที่จะเรียก `signal()` เพื่อให้ได้ทูเพิลที่มีตัวอ่านและตัวเขียน เรากลับใช้ `RwSignal::new()` เพื่อให้ได้สัญญาณที่อ่าน-เขียนได้ในตัวเดียว ซึ่งสะดวกกว่าสำหรับสถานการณ์ที่ถ้าไม่ทำแบบนี้เราก็ต้องส่งทูเพิลไปมา

```rust
// each item manages a reactive view
// but the list itself will never change
let counter_buttons = counters
    .map(|count| {
        view! {
            <li>
                <button
                    on:click=move |_| *count.write() += 1
                >
                    {count}
                </button>
            </li>
        }
    })
    .collect_view();

view! {
    <ul>{counter_buttons}</ul>
}
```

คุณ *สามารถ* เรนเดอร์ `Fn() -> Vec<_>` แบบรีแอกทีฟได้เช่นกัน แต่พึงสังเกตว่านี่คือการอัปเดตรายการแบบไม่มีคีย์ (unkeyed) มันจะนำเอลิเมนต์ DOM ที่มีอยู่เดิมกลับมาใช้ซ้ำ แล้วอัปเดตด้วยค่าใหม่ตามลำดับของมันใน `Vec<_>` ใหม่ ถ้าคุณแค่เพิ่มและลบไอเท็มที่ส่วนท้ายของรายการ วิธีนี้ก็ใช้ได้ดี แต่ถ้าคุณย้ายไอเท็มไปมา หรือแทรกไอเท็มเข้าไปตรงกลางรายการ สิ่งนี้จะทำให้เบราว์เซอร์ทำงานมากเกินความจำเป็น และอาจส่งผลที่คาดไม่ถึงต่อสถานะของอินพุตและแอนิเมชัน CSS (สำหรับรายละเอียดเพิ่มเติมเกี่ยวกับความแตกต่างระหว่างแบบ "มีคีย์" (keyed) กับ "ไม่มีคีย์" (unkeyed) พร้อมตัวอย่างที่ใช้ได้จริง คุณสามารถอ่าน[บทความนี้](https://www.stefankrause.net/wp/?p=342)ได้)

โชคดีที่ยังมีวิธีที่มีประสิทธิภาพสำหรับการวนซ้ำรายการแบบมีคีย์เช่นกัน

## การเรนเดอร์แบบไดนามิกด้วยคอมโพเนนต์ `<For/>`

คอมโพเนนต์ [`<For/>`](https://docs.rs/leptos/latest/leptos/control_flow/fn.For.html) คือรายการไดนามิกแบบมีคีย์ โดยรับพร็อพสามตัว:

- `each`: ฟังก์ชันรีแอกทีฟที่คืนค่าไอเท็ม `T` ที่จะถูกวนซ้ำ
- `key`: ฟังก์ชันคีย์ที่รับ `&T` แล้วคืนค่าคีย์หรือ ID ที่เสถียรและไม่ซ้ำกัน
- `children` (ลูก): เรนเดอร์แต่ละ `T` ให้เป็นวิว

`key` ก็คือคีย์นั่นแหละ คุณสามารถเพิ่ม ลบ และย้ายไอเท็มภายในรายการได้ ตราบใดที่คีย์ของแต่ละไอเท็มคงที่ตลอดเวลา เฟรมเวิร์กไม่จำเป็นต้องเรนเดอร์ไอเท็มใดซ้ำ นอกจากไอเท็มที่เพิ่งเพิ่มเข้ามาใหม่ และมันสามารถเพิ่ม ลบ และย้ายไอเท็มได้อย่างมีประสิทธิภาพสูงเมื่อมีการเปลี่ยนแปลง สิ่งนี้ทำให้การอัปเดตรายการมีประสิทธิภาพมากที่สุดเมื่อรายการเปลี่ยนไป โดยทำงานเพิ่มเพียงเล็กน้อยเท่านั้น

การสร้าง `key` ที่ดีอาจยุ่งยากสักหน่อย โดยทั่วไปคุณ *ไม่* ควรใช้อินเด็กซ์เพื่อจุดประสงค์นี้ เพราะมันไม่เสถียร - ถ้าคุณลบหรือย้ายไอเท็ม อินเด็กซ์ของไอเท็มเหล่านั้นก็จะเปลี่ยนไป

แต่การทำอะไรอย่างการสร้าง ID ที่ไม่ซ้ำกันให้กับแต่ละแถวตอนที่มันถูกสร้างขึ้น แล้วใช้ ID นั้นเป็นคีย์ให้กับฟังก์ชัน key ก็เป็นไอเดียที่ดีมาก

ลองดูตัวอย่างได้ที่คอมโพเนนต์ `<DynamicList/>` ด้านล่างนี้

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/4-iteration-0-7-dw4dfl?file=%2Fsrc%2Fmain.rs%3A1%2C1-159%2C1&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/4-iteration-0-7-dw4dfl?file=%2Fsrc%2Fmain.rs%3A1%2C1-159%2C1&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;

// Iteration is a very common task in most applications.
// So how do you take a list of data and render it in the DOM?
// This example will show you the two ways:
// 1) for mostly-static lists, using Rust iterators
// 2) for lists that grow, shrink, or move items, using <For/>

#[component]
fn App() -> impl IntoView {
    view! {
        <h1>"Iteration"</h1>
        <h2>"Static List"</h2>
        <p>"Use this pattern if the list itself is static."</p>
        <StaticList length=5/>
        <h2>"Dynamic List"</h2>
        <p>"Use this pattern if the rows in your list will change."</p>
        <DynamicList initial_length=5/>
    }
}

/// A list of counters, without the ability
/// to add or remove any.
#[component]
fn StaticList(
    /// How many counters to include in this list.
    length: usize,
) -> impl IntoView {
    // create counter signals that start at incrementing numbers
    let counters = (1..=length).map(|idx| RwSignal::new(idx));

    // when you have a list that doesn't change, you can
    // manipulate it using ordinary Rust iterators
    // and collect it into a Vec<_> to insert it into the DOM
    let counter_buttons = counters
        .map(|count| {
            view! {
                <li>
                    <button
                        on:click=move |_| *count.write() += 1
                    >
                        {count}
                    </button>
                </li>
            }
        })
        .collect::<Vec<_>>();

    // Note that if `counter_buttons` were a reactive list
    // and its value changed, this would be very inefficient:
    // it would rerender every row every time the list changed.
    view! {
        <ul>{counter_buttons}</ul>
    }
}

/// A list of counters that allows you to add or
/// remove counters.
#[component]
fn DynamicList(
    /// The number of counters to begin with.
    initial_length: usize,
) -> impl IntoView {
    // This dynamic list will use the <For/> component.
    // <For/> is a keyed list. This means that each row
    // has a defined key. If the key does not change, the row
    // will not be re-rendered. When the list changes, only
    // the minimum number of changes will be made to the DOM.

    // `next_counter_id` will let us generate unique IDs
    // we do this by simply incrementing the ID by one
    // each time we create a counter
    let mut next_counter_id = initial_length;

    // we generate an initial list as in <StaticList/>
    // but this time we include the ID along with the signal
    // see NOTE in add_counter below re: ArcRwSignal
    let initial_counters = (0..initial_length)
        .map(|id| (id, ArcRwSignal::new(id + 1)))
        .collect::<Vec<_>>();

    // now we store that initial list in a signal
    // this way, we'll be able to modify the list over time,
    // adding and removing counters, and it will change reactively
    let (counters, set_counters) = signal(initial_counters);

    let add_counter = move |_| {
        // create a signal for the new counter
        // we use ArcRwSignal here, instead of RwSignal
        // ArcRwSignal is a reference-counted type, rather than the arena-allocated
        // signal types we've been using so far.
        // When we're creating a collection of signals like this, using ArcRwSignal
        // allows each signal to be deallocated when its row is removed.
        let sig = ArcRwSignal::new(next_counter_id + 1);
        // add this counter to the list of counters
        set_counters.update(move |counters| {
            // since `.update()` gives us `&mut T`
            // we can just use normal Vec methods like `push`
            counters.push((next_counter_id, sig))
        });
        // increment the ID so it's always unique
        next_counter_id += 1;
    };

    view! {
        <div>
            <button on:click=add_counter>
                "Add Counter"
            </button>
            <ul>
                // The <For/> component is central here
                // This allows for efficient, key list rendering
                <For
                    // `each` takes any function that returns an iterator
                    // this should usually be a signal or derived signal
                    // if it's not reactive, just render a Vec<_> instead of <For/>
                    each=move || counters.get()
                    // the key should be unique and stable for each row
                    // using an index is usually a bad idea, unless your list
                    // can only grow, because moving items around inside the list
                    // means their indices will change and they will all rerender
                    key=|counter| counter.0
                    // `children` receives each item from your `each` iterator
                    // and returns a view
                    children=move |(id, count)| {
                        // we can convert our ArcRwSignal to a Copy-able RwSignal
                        // for nicer DX when moving it into the view
                        let count = RwSignal::from(count);
                        view! {
                            <li>
                                <button
                                    on:click=move |_| *count.write() += 1
                                >
                                    {count}
                                </button>
                                <button
                                    on:click=move |_| {
                                        set_counters
                                            .write()
                                            .retain(|(counter_id, _)| {
                                                counter_id != &id
                                            });
                                    }
                                >
                                    "Remove"
                                </button>
                            </li>
                        }
                    }
                />
            </ul>
        </div>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>

### การเข้าถึงอินเด็กซ์ระหว่างการวนซ้ำด้วย `<ForEnumerate/>`

ในกรณีที่คุณต้องการเข้าถึงอินเด็กซ์แบบเรียลไทม์ระหว่างการวนซ้ำ Leptos มีคอมโพเนนต์ [`<ForEnumerate/>`](https://docs.rs/leptos/latest/leptos/control_flow/fn.ForEnumerate.html) ให้ใช้

พร็อพต่างๆ เหมือนกับคอมโพเนนต์ [`<For/>`](https://docs.rs/leptos/latest/leptos/control_flow/fn.For.html) ทุกประการ แต่เมื่อเรนเดอร์ `children` มันจะเพิ่มพารามิเตอร์ `ReadSignal<usize>` เป็นอินเด็กซ์ให้ด้วย:

```rust
#[derive(Copy, Clone, Debug, PartialEq, Eq)]
struct Counter {
  id: usize,
  count: RwSignal<i32>
}

<ForEnumerate
    each=move || counters.get() // Same as <For/>
    key=|counter| counter.id    // Same as <For/>
    // Provides the index as a signal and the child T
    children={move |index: ReadSignal<usize>, counter: Counter| {
        view! {
            <button>{move || index.get()} ". Value: " {move || counter.count.get()}</button>
        }
    }}
/>
```

หรือจะใช้กับไวยากรณ์ `let` ที่สะดวกกว่าก็ได้เช่นกัน:
```rust
<ForEnumerate
    each=move || counters.get() // Same as <For/>
    key=|counter| counter.id    // Same as <For/>
    let(idx, counter)           // let syntax
>
    <button>{move || idx.get()} ". Value: " {move || counter.count.get()}</button>
</ ForEnumerate>
```
